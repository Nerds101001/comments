"""
Gmail API integration (optional — for writing style learning).

OAuth flow:
  GET  /api/gmail/auth       — redirect to Google OAuth consent screen
  GET  /api/gmail/callback   — handle OAuth callback, store token
  POST /api/gmail/sync       — fetch Mukul's sent emails, extract style samples
  GET  /api/gmail/status     — connection status

The tokens are stored in the app_settings table.
"""
from __future__ import annotations
import json
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AppSetting
from app.schemas import StatusResponse
from app.config import settings
from app.services import style_learner

router = APIRouter(prefix="/api/gmail", tags=["gmail"])
logger = logging.getLogger(__name__)

GMAIL_TOKEN_KEY = "gmail_token"
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]


def _get_flow():
    """Build Google OAuth flow object."""
    try:
        from google_auth_oauthlib.flow import Flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "redirect_uris": [settings.GMAIL_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=GMAIL_SCOPES,
        )
        flow.redirect_uri = settings.GMAIL_REDIRECT_URI
        return flow
    except ImportError:
        raise HTTPException(500, "google-auth-oauthlib not installed. Run: pip install google-auth-oauthlib")


# ── AUTH ──────────────────────────────────────────────────────────────────────
@router.get("/auth")
async def gmail_auth():
    if not settings.GMAIL_CLIENT_ID:
        raise HTTPException(400, "Gmail Client ID not configured. Add GMAIL_CLIENT_ID to .env")
    flow = _get_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return RedirectResponse(auth_url)


@router.get("/callback")
async def gmail_callback(code: str, db: AsyncSession = Depends(get_db)):
    flow = _get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes or []),
    }

    # Store token in DB
    existing = await db.execute(select(AppSetting).where(AppSetting.key == GMAIL_TOKEN_KEY))
    row = existing.scalar_one_or_none()
    if row:
        row.value = json.dumps(token_data)
    else:
        db.add(AppSetting(key=GMAIL_TOKEN_KEY, value=json.dumps(token_data)))
    await db.commit()

    return {"status": "connected", "message": "Gmail connected. Go to /api/gmail/sync to import writing style."}


# ── STATUS ────────────────────────────────────────────────────────────────────
@router.get("/status", response_model=StatusResponse)
async def gmail_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppSetting).where(AppSetting.key == GMAIL_TOKEN_KEY))
    row = result.scalar_one_or_none()
    return StatusResponse(
        status="connected" if row else "not_connected",
        data={"configured": bool(settings.GMAIL_CLIENT_ID)},
    )


# ── SYNC EMAILS ───────────────────────────────────────────────────────────────
@router.post("/sync", response_model=StatusResponse)
async def sync_gmail(
    max_emails: int = 100,
    query: str = "in:sent",
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch Mukul's sent emails and extract style samples.
    Short emails (< 300 chars) that look like sales messages are stored as StyleSamples.
    """
    result = await db.execute(select(AppSetting).where(AppSetting.key == GMAIL_TOKEN_KEY))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(400, "Gmail not connected. Visit /api/gmail/auth first.")

    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import base64, email as email_lib

        token_data = json.loads(row.value)
        creds = Credentials(**{k: token_data[k] for k in token_data if k != "scopes"})
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)

        msgs = service.users().messages().list(
            userId="me", q=query, maxResults=max_emails
        ).execute().get("messages", [])

        imported = 0
        for m in msgs:
            msg_data = service.users().messages().get(
                userId="me", id=m["id"], format="full"
            ).execute()

            # Extract plain text body
            body_text = _extract_body(msg_data)
            if not body_text or len(body_text) < 20 or len(body_text) > 1500:
                continue
            # Filter to likely sales/business emails (skip newsletters etc.)
            lower = body_text.lower()
            if any(w in lower for w in ["unsubscribe", "newsletter", "noreply", "no-reply"]):
                continue

            await style_learner.add_sample(
                db,
                text=body_text[:800],
                source="gmail",
                rep_language=_detect_language(body_text),
                context_type="email",
            )
            imported += 1

        return StatusResponse(
            status="ok",
            message=f"Imported {imported} emails as style samples",
            data={"imported": imported},
        )

    except Exception as exc:
        logger.error("Gmail sync failed: %s", exc)
        raise HTTPException(500, str(exc))


def _extract_body(msg_data: dict) -> str:
    """Extract plain text from Gmail message payload."""
    payload = msg_data.get("payload", {})

    def _get_text(part):
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                import base64
                return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
        for sub in part.get("parts", []):
            text = _get_text(sub)
            if text:
                return text
        return ""

    return _get_text(payload).strip()


def _detect_language(text: str) -> str:
    """Heuristic: count Hindi words to pick language bucket."""
    hindi_words = ["toh", "achha", "theek", "lekin", "aur", "hai", "hain",
                   "karo", "kiya", "kal", "abhi", "yaar", "ji", "na", "bhi"]
    lower = text.lower()
    count = sum(1 for w in hindi_words if f" {w} " in lower or lower.startswith(w + " "))
    if count >= 6:
        return "hinglish_60"
    if count >= 2:
        return "hinglish_80"
    return "english_only"
