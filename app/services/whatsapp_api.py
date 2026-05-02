"""
Meta WhatsApp Cloud API client.

Docs: https://developers.facebook.com/docs/whatsapp/cloud-api

Endpoints used:
  POST /{version}/{phone_number_id}/messages   — send message
  GET  /webhook                                — Meta verification challenge
  POST /webhook                                — incoming message events
"""
from __future__ import annotations
import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

WA_BASE = "https://graph.facebook.com"


def _url(path: str) -> str:
    return f"{WA_BASE}/{settings.WHATSAPP_API_VERSION}/{path}"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


# ─────────────────────────────────────────────────────────
#  SEND TEXT MESSAGE
# ─────────────────────────────────────────────────────────
async def send_text(to: str, text: str) -> dict:
    """
    Send a plain text WhatsApp message.
    `to` must be the phone number with country code, no + (e.g. '919812345001').
    Returns Meta API response dict.
    """
    if not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_ACCESS_TOKEN:
        logger.warning("WhatsApp not configured — message not sent to %s", to)
        return {"status": "not_configured"}

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to),
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            _url(f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"),
            headers=_headers(),
            json=payload,
        )
        data = resp.json()
        if resp.status_code != 200:
            logger.error("WhatsApp send failed: %s", data)
            raise RuntimeError(f"WhatsApp API error {resp.status_code}: {data}")
        logger.info("WhatsApp sent to %s — msg_id=%s", to, data.get("messages", [{}])[0].get("id"))
        return data


# ─────────────────────────────────────────────────────────
#  WEBHOOK VERIFICATION (GET)
# ─────────────────────────────────────────────────────────
def verify_webhook(
    mode: str,
    token: str,
    challenge: str,
) -> Optional[str]:
    """
    Meta sends a GET to the webhook URL when you first configure it.
    Returns the challenge string if valid, else None.
    """
    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return challenge
    logger.warning("WhatsApp webhook verification failed (mode=%s, token=%s)", mode, token)
    return None


# ─────────────────────────────────────────────────────────
#  PARSE INCOMING WEBHOOK EVENT (POST)
# ─────────────────────────────────────────────────────────
def parse_incoming_message(payload: dict) -> Optional[dict]:
    """
    Extract the relevant info from a Meta webhook POST payload.
    Returns a normalised dict or None if no text message found.

    Normalised dict:
    {
        "from":       str,   # sender phone (e.g. '919812345001')
        "wa_msg_id":  str,   # WhatsApp message ID
        "text":       str,   # message text
        "timestamp":  str,   # unix timestamp as string
        "name":       str,   # sender display name (if available)
    }
    """
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                val = change.get("value", {})
                messages = val.get("messages", [])
                contacts = {c["wa_id"]: c["profile"]["name"] for c in val.get("contacts", [])}
                for msg in messages:
                    if msg.get("type") != "text":
                        continue
                    sender = msg.get("from", "")
                    return {
                        "from":      sender,
                        "wa_msg_id": msg.get("id", ""),
                        "text":      msg["text"]["body"],
                        "timestamp": msg.get("timestamp", ""),
                        "name":      contacts.get(sender, ""),
                    }
    except (KeyError, TypeError, IndexError) as exc:
        logger.warning("Failed to parse WhatsApp webhook payload: %s", exc)
    return None
