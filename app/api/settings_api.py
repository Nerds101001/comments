"""
Settings & team management API routes.
"""
from __future__ import annotations
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Rep, Senior, AppSetting
from app.schemas import RepOut, RepCreate, SeniorOut, SeniorCreate, SettingsOut, StatusResponse
from app.config import settings
from app.services import crm_client, whatsapp_api

router = APIRouter(prefix="/api/settings", tags=["settings"])


# ── FULL SETTINGS DUMP ────────────────────────────────────────────────────────
@router.get("", response_model=SettingsOut)
async def get_settings(db: AsyncSession = Depends(get_db)):
    team = (await db.execute(select(Rep).order_by(Rep.id))).scalars().all()
    seniors = (await db.execute(select(Senior).order_by(Senior.id))).scalars().all()

    return SettingsOut(
        team=list(team),
        seniors=list(seniors),
        integrations={
            "claude": {
                "connected": bool(settings.CLAUDE_API_KEY),
                "model": settings.CLAUDE_MODEL,
                "api_key_preview": (settings.CLAUDE_API_KEY[:8] + "...") if settings.CLAUDE_API_KEY else "",
            },
            "whatsapp": {
                "connected": bool(settings.WHATSAPP_PHONE_NUMBER_ID and settings.WHATSAPP_ACCESS_TOKEN),
                "phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID,
                "verify_token": settings.WHATSAPP_VERIFY_TOKEN,
            },
            "crm": {
                "connected": bool(settings.CRM_TOKEN or settings.CRM_USERNAME),
                "base_url": settings.CRM_BASE_URL,
                "poll_interval_minutes": settings.CRM_POLL_INTERVAL_MINUTES,
            },
            "gmail": {
                "connected": False,  # checked via /api/gmail/status
                "client_id_set": bool(settings.GMAIL_CLIENT_ID),
            },
        },
        escalation_rules={
            "ai_confidence_threshold": settings.AI_CONFIDENCE_THRESHOLD,
            "pricing_authority_pct": settings.PRICING_AUTHORITY_PCT,
            "key_account_ltv_threshold": settings.KEY_ACCOUNT_LTV_THRESHOLD,
        },
        senior_layer={
            "escalation_window_hours": settings.SENIOR_ESCALATION_WINDOW_HOURS,
        },
    )


# ── TEAM ──────────────────────────────────────────────────────────────────────
@router.get("/team", response_model=List[RepOut])
async def list_team(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rep).order_by(Rep.id))
    return result.scalars().all()


@router.get("/team/{rep_id}", response_model=RepOut)
async def get_rep(rep_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rep).where(Rep.id == rep_id))
    rep = result.scalar_one_or_none()
    if not rep:
        raise HTTPException(404, "Rep not found")
    return rep


@router.put("/team/{rep_id}", response_model=RepOut)
async def update_rep(rep_id: str, body: RepCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rep).where(Rep.id == rep_id))
    rep = result.scalar_one_or_none()
    if not rep:
        raise HTTPException(404, "Rep not found")
    for k, v in body.model_dump(exclude={"id"}).items():
        setattr(rep, k, v)
    await db.commit()
    await db.refresh(rep)
    return rep


@router.post("/team", response_model=RepOut)
async def create_rep(body: RepCreate, db: AsyncSession = Depends(get_db)):
    rep = Rep(**body.model_dump())
    db.add(rep)
    await db.commit()
    await db.refresh(rep)
    return rep


# ── SENIORS ───────────────────────────────────────────────────────────────────
@router.get("/seniors", response_model=List[SeniorOut])
async def list_seniors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Senior).order_by(Senior.id))
    return result.scalars().all()


@router.put("/seniors/{senior_id}", response_model=SeniorOut)
async def update_senior(senior_id: str, body: SeniorCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Senior).where(Senior.id == senior_id))
    senior = result.scalar_one_or_none()
    if not senior:
        raise HTTPException(404, "Senior not found")
    for k, v in body.model_dump(exclude={"id"}).items():
        setattr(senior, k, v)
    await db.commit()
    await db.refresh(senior)
    return senior


# ── TEST CONNECTIONS ──────────────────────────────────────────────────────────
@router.post("/test/{integration}", response_model=StatusResponse)
async def test_integration(integration: str):
    if integration == "crm":
        result = await crm_client.test_connection()
        return StatusResponse(
            status="connected" if result["connected"] else "error",
            data=result,
        )
    if integration == "whatsapp":
        configured = bool(settings.WHATSAPP_PHONE_NUMBER_ID and settings.WHATSAPP_ACCESS_TOKEN)
        return StatusResponse(
            status="connected" if configured else "not_configured",
            data={"configured": configured, "phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID},
        )
    if integration == "claude":
        if not settings.CLAUDE_API_KEY:
            return StatusResponse(status="not_configured", message="No API key set")
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    settings.CLAUDE_API_URL,
                    headers={
                        "x-api-key": settings.CLAUDE_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": settings.CLAUDE_MODEL,
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "ping"}],
                    },
                )
                if resp.status_code == 200:
                    return StatusResponse(status="connected", message=f"Claude {settings.CLAUDE_MODEL} OK")
                return StatusResponse(status="error", message=f"API returned {resp.status_code}")
        except Exception as exc:
            return StatusResponse(status="error", message=str(exc))

    raise HTTPException(400, f"Unknown integration: {integration}")
