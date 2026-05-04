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
    
    # Mask password for display (show ••••••••)
    smtp_password_masked = "••••••••" if smtp_password else ""

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
                "password": smtp_password_masked,
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
                AppSetting.key.in_(["smtp_host", "smtp_port", "smtp_user", "smtp_password", "smtp_from_name", "smtp_from_address"])
            )
        )
        smtp_settings_db = {s.key: s.value for s in smtp_settings_result.scalars().all()}
        
        smtp_host = smtp_settings_db.get("smtp_host", settings.EMAIL_SMTP_HOST)
        smtp_port = int(smtp_settings_db.get("smtp_port", settings.EMAIL_SMTP_PORT))
        smtp_user = smtp_settings_db.get("smtp_user", settings.EMAIL_SMTP_USER)
        smtp_password = smtp_settings_db.get("smtp_password", settings.EMAIL_SMTP_PASSWORD)
        smtp_from_name = smtp_settings_db.get("smtp_from_name", settings.EMAIL_FROM_NAME)
        smtp_from_address = smtp_settings_db.get("smtp_from_address", settings.EMAIL_FROM_ADDRESS) or smtp_user
        
        if not smtp_host or not smtp_user or not smtp_password:
            return StatusResponse(status="not_configured", message="SMTP not configured")
        
        try:
            import smtplib
            import ssl
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create test email
            msg = MIMEMultipart()
            msg['From'] = f"{smtp_from_name} <{smtp_from_address}>"
            msg['To'] = "csenerds@gmail.com"
            msg['Subject'] = "Hi-Tech AI Sales - SMTP Test Email"
            
            body = """
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #007AFF;">✅ SMTP Connection Successful!</h2>
                <p>This is a test email from your Hi-Tech AI Sales system.</p>
                <p><strong>SMTP Configuration:</strong></p>
                <ul>
                    <li>Host: {host}</li>
                    <li>Port: {port}</li>
                    <li>User: {user}</li>
                </ul>
                <p style="color: #34C759; font-weight: bold;">Your email system is working correctly!</p>
                <hr style="border: 1px solid #E5E5EA; margin: 20px 0;">
                <p style="color: #86868B; font-size: 12px;">Sent from Hi-Tech AI Sales Org</p>
            </body>
            </html>
            """.format(host=smtp_host, port=smtp_port, user=smtp_user)
            
            msg.attach(MIMEText(body, 'html'))
            
            # Try different connection methods
            try:
                # Method 1: STARTTLS (port 587)
                if smtp_port == 587:
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
                    server.quit()
                # Method 2: SSL (port 465)
                elif smtp_port == 465:
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=15)
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
                    server.quit()
                # Method 3: Plain (port 25 or other)
                else:
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
                    server.login(smtp_user, smtp_password)
                    server.send_message(msg)
                    server.quit()
                
                return StatusResponse(
                    status="connected", 
                    message=f"✅ Test email sent successfully to csenerds@gmail.com"
                )
            except smtplib.SMTPAuthenticationError as e:
                return StatusResponse(status="error", message=f"Authentication failed: {str(e)}")
            except smtplib.SMTPConnectError as e:
                return StatusResponse(status="error", message=f"Connection failed: {str(e)}")
            except Exception as e:
                return StatusResponse(status="error", message=f"SMTP error: {str(e)}")
                
        except Exception as exc:
            return StatusResponse(status="error", message=f"SMTP test failed: {str(exc)}")
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
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """Save SMTP settings to database."""
    from datetime import datetime
    from fastapi import Body
    
    # Extract values from request body
    host = request.get("host", "")
    port = request.get("port", 587)
    user = request.get("user", "")
    password = request.get("password", "")
    from_name = request.get("from_name", "Hi-Tech AI Sales")
    from_address = request.get("from_address", "")
    
    if not host or not user:
        raise HTTPException(400, "Missing required fields: host, user")

    smtp_settings = {
        "smtp_host": host,
        "smtp_port": str(port),
        "smtp_user": user,
        "smtp_from_name": from_name,
        "smtp_from_address": from_address or user,
    }
    # Only update password if a new one was provided
    if password:
        smtp_settings["smtp_password"] = password
    
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
