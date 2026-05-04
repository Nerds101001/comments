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

    # Get SMTP settings from database
    smtp_settings_result = await db.execute(
        select(AppSetting).where(
            AppSetting.key.in_(["smtp_host", "smtp_port", "smtp_user", "smtp_password", "smtp_from_name", "smtp_from_address"])
        )
    )
    smtp_settings_db = {s.key: s.value for s in smtp_settings_result.scalars().all()}
    
    smtp_host = smtp_settings_db.get("smtp_host", settings.EMAIL_SMTP_HOST)
    smtp_user = smtp_settings_db.get("smtp_user", settings.EMAIL_SMTP_USER)
    smtp_password = smtp_settings_db.get("smtp_password", settings.EMAIL_SMTP_PASSWORD)

    return SettingsOut(
        team=list(team),
        seniors=list(seniors),
        integrations={
            "ai": {
                "connected": bool(settings.AI_API_KEY),
                "provider": settings.AI_PROVIDER,
                "model": settings.AI_MODEL,
                "api_key_preview": (settings.AI_API_KEY[:8] + "...") if settings.AI_API_KEY else "",
            },
            "whatsapp": {
                "connected": bool(settings.WHATSAPP_PHONE_NUMBER_ID and settings.WHATSAPP_ACCESS_TOKEN),
                "phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID,
                "verify_token": settings.WHATSAPP_VERIFY_TOKEN,
            },
            "crm": {
                "connected": bool(settings.CRM_USERNAME and settings.CRM_PASSWORD),
                "base_url": settings.CRM_BASE_URL,
                "poll_interval_minutes": settings.CRM_POLL_INTERVAL_MINUTES,
            },
            "gmail": {
                "connected": False,  # checked via /api/gmail/status
                "client_id_set": bool(settings.GMAIL_CLIENT_ID),
            },
            "smtp": {
                "connected": bool(smtp_host and smtp_user and smtp_password),
                "host": smtp_host,
                "port": smtp_settings_db.get("smtp_port", str(settings.EMAIL_SMTP_PORT)),
                "user": smtp_user,
                "from_name": smtp_settings_db.get("smtp_from_name", settings.EMAIL_FROM_NAME),
                "from_address": smtp_settings_db.get("smtp_from_address", settings.EMAIL_FROM_ADDRESS),
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
async def test_integration(integration: str, db: AsyncSession = Depends(get_db)):
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
    if integration == "smtp":
        # Get SMTP settings from database
        smtp_settings_result = await db.execute(
            select(AppSetting).where(
                AppSetting.key.in_(["smtp_host", "smtp_port", "smtp_user", "smtp_password"])
            )
        )
        smtp_settings_db = {s.key: s.value for s in smtp_settings_result.scalars().all()}
        
        smtp_host = smtp_settings_db.get("smtp_host", settings.EMAIL_SMTP_HOST)
        smtp_port = int(smtp_settings_db.get("smtp_port", settings.EMAIL_SMTP_PORT))
        smtp_user = smtp_settings_db.get("smtp_user", settings.EMAIL_SMTP_USER)
        smtp_password = smtp_settings_db.get("smtp_password", settings.EMAIL_SMTP_PASSWORD)
        
        if not smtp_host or not smtp_user or not smtp_password:
            return StatusResponse(status="not_configured", message="SMTP not configured")
        
        try:
            import smtplib
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.quit()
            return StatusResponse(status="connected", message="SMTP connection successful")
        except Exception as exc:
            return StatusResponse(status="error", message=f"SMTP connection failed: {str(exc)}")
    if integration == "ai":
        if not settings.AI_API_KEY:
            return StatusResponse(status="not_configured", message="No API key set")
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                # Test based on provider
                if settings.AI_PROVIDER == "nvidia":
                    # NVIDIA API test
                    resp = await client.post(
                        f"{settings.AI_BASE_URL}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.AI_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": settings.AI_MODEL,
                            "messages": [{"role": "user", "content": "ping"}],
                            "max_tokens": 10,
                        },
                    )
                else:
                    # Claude API test
                    resp = await client.post(
                        f"{settings.AI_BASE_URL}/messages",
                        headers={
                            "x-api-key": settings.AI_API_KEY,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json",
                        },
                        json={
                            "model": settings.AI_MODEL,
                            "max_tokens": 10,
                            "messages": [{"role": "user", "content": "ping"}],
                        },
                    )
                
                if resp.status_code == 200:
                    return StatusResponse(
                        status="connected", 
                        message=f"{settings.AI_PROVIDER.upper()} {settings.AI_MODEL} OK"
                    )
                return StatusResponse(status="error", message=f"API returned {resp.status_code}")
        except Exception as exc:
            return StatusResponse(status="error", message=str(exc))

    raise HTTPException(400, f"Unknown integration: {integration}")


# ── SAVE SMTP SETTINGS ────────────────────────────────────────────────────────
@router.post("/smtp", response_model=StatusResponse)
async def save_smtp_settings(
    host: str,
    port: int,
    user: str,
    password: str,
    from_name: str = "Hi-Tech AI Sales",
    from_address: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Save SMTP settings to database."""
    from datetime import datetime
    
    smtp_settings = {
        "smtp_host": host,
        "smtp_port": str(port),
        "smtp_user": user,
        "smtp_password": password,
        "smtp_from_name": from_name,
        "smtp_from_address": from_address or user,
    }
    
    for key, value in smtp_settings.items():
        result = await db.execute(
            select(AppSetting).where(AppSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = AppSetting(
                key=key,
                value=value,
                updated_at=datetime.utcnow()
            )
            db.add(setting)
    
    await db.commit()
    
    return StatusResponse(
        status="ok",
        message="SMTP settings saved successfully",
        data={"host": host, "port": port, "user": user}
    )
