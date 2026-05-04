"""
AiSensy WhatsApp API client.

Docs: https://documenter.getpostman.com/view/aisensy/collection

Endpoints used:
  POST https://backend.aisensy.com/campaign/t1/api/v2  — send template message
"""
from __future__ import annotations
import logging
from typing import Optional, List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

AISENSY_BASE = "https://backend.aisensy.com/campaign/t1/api/v2"


async def send_message(
    destination: str,
    campaign_name: str,
    template_params: Optional[List[str]] = None,
    media_url: Optional[str] = None,
    media_filename: Optional[str] = None,
) -> dict:
    """
    Send a WhatsApp message via AiSensy.

    Args:
        destination: Phone with country code, no + (e.g. '919812345001')
        campaign_name: AiSensy campaign/template name (must be pre-approved)
        template_params: Variable values for the template ({{1}}, {{2}}, ...)
        media_url: Optional media attachment URL
        media_filename: Filename for media attachment

    Returns:
        AiSensy API response dict
    """
    if not settings.AISENSY_API_KEY:
        logger.warning("AiSensy not configured — message not sent to %s", destination)
        return {"status": "not_configured"}

    payload = {
        "apiKey": settings.AISENSY_API_KEY,
        "campaignName": campaign_name,
        "destination": str(destination),
        "userName": settings.AISENSY_USERNAME,
        "templateParams": template_params or [],
        "source": "hi-tech-ai-sales",
        "media": {},
        "buttons": [],
        "carouselCards": [],
        "location": {},
    }

    if media_url:
        payload["media"] = {
            "url": media_url,
            "filename": media_filename or "attachment",
        }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            AISENSY_BASE,
            headers={"Content-Type": "application/json"},
            json=payload,
        )
        data = resp.json()
        if resp.status_code not in (200, 201):
            logger.error("AiSensy send failed (%s): %s", resp.status_code, data)
            raise RuntimeError(f"AiSensy API error {resp.status_code}: {data}")
        logger.info("AiSensy sent to %s via campaign '%s'", destination, campaign_name)
        return data


async def send_text_notification(destination: str, message: str) -> dict:
    """
    Convenience wrapper: send a plain text message using the default
    'hi_tech_notification' campaign template where {{1}} = message body.
    Create this template in AiSensy dashboard first.
    """
    return await send_message(
        destination=destination,
        campaign_name="hi_tech_notification",
        template_params=[message],
    )


async def test_connection() -> dict:
    """Validate the API key by making a minimal request."""
    if not settings.AISENSY_API_KEY:
        return {"connected": False, "error": "AISENSY_API_KEY not set"}
    try:
        # AiSensy doesn't have a dedicated status endpoint; attempt a dry-run
        # by sending to a known-invalid number — we just check if auth passes
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                AISENSY_BASE,
                headers={"Content-Type": "application/json"},
                json={
                    "apiKey": settings.AISENSY_API_KEY,
                    "campaignName": "test",
                    "destination": "910000000000",
                    "userName": settings.AISENSY_USERNAME,
                    "templateParams": [],
                    "source": "test",
                },
            )
            data = resp.json()
            # 401/403 = bad key; anything else = key is valid (destination invalid is ok)
            if resp.status_code in (401, 403):
                return {"connected": False, "error": data.get("message", "Invalid API key")}
            return {"connected": True, "response_code": resp.status_code}
    except Exception as exc:
        return {"connected": False, "error": str(exc)}
