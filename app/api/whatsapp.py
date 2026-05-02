"""
WhatsApp API routes.

GET  /api/whatsapp/webhook   — Meta verification challenge
POST /api/whatsapp/webhook   — Incoming messages from reps/customers
POST /api/whatsapp/send      — Manual send (from frontend Send button)
GET  /api/whatsapp/status    — Connection status
"""
from __future__ import annotations
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Conversation, Message, Rep
from app.schemas import WhatsAppSendRequest, StatusResponse
from app.services import whatsapp_api
from app.config import settings

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])
logger = logging.getLogger(__name__)


# ── WEBHOOK VERIFICATION (Meta sends GET when you configure the webhook) ─────
@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    challenge = whatsapp_api.verify_webhook(
        mode=hub_mode or "",
        token=hub_verify_token or "",
        challenge=hub_challenge or "",
    )
    if challenge is None:
        raise HTTPException(status_code=403, detail="Webhook verification failed")
    return Response(content=challenge, media_type="text/plain")


# ── INCOMING MESSAGES (Meta sends POST for every incoming message) ────────────
@router.post("/webhook")
async def receive_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Process incoming WhatsApp messages from reps.
    Matches the sender's phone number to a Rep in the database,
    finds the most recent active conversation for that rep,
    and adds the incoming message.
    """
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ignored"}

    event = whatsapp_api.parse_incoming_message(payload)
    if not event:
        return {"status": "ignored", "reason": "not a text message"}

    sender_phone = event["from"]
    msg_text = event["text"]

    # Match to a rep
    rep_result = await db.execute(select(Rep).where(Rep.phone == sender_phone))
    rep = rep_result.scalar_one_or_none()
    if not rep:
        logger.info("Unknown sender %s — ignoring", sender_phone)
        return {"status": "ignored", "reason": "unknown sender"}

    # Find most recent active conversation for this rep
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.rep_id == rep.id, Conversation.is_resolved == False)  # noqa
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )
    conv = conv_result.scalar_one_or_none()
    if not conv:
        logger.info("No active conversation for rep %s — ignoring incoming message", rep.id)
        return {"status": "ignored", "reason": "no active conversation"}

    # Add message to conversation
    msg = Message(
        conversation_id=conv.id,
        from_who="rep",
        text=msg_text,
        ts=datetime.utcnow().strftime("%H:%M"),
        date_label="today",
        status="received",
        is_read=False,
        by_ai=False,
        by_mukul_real=False,
        whatsapp_msg_id=event.get("wa_msg_id"),
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    conv.updated_at = datetime.utcnow()
    await db.commit()

    # Handle reply scoring for CRM follow-up threads
    from app.api.conversations import _handle_rep_reply
    # Re-load conv with relationships
    from sqlalchemy.orm import selectinload
    conv_full_result = await db.execute(
        select(Conversation)
        .options(
            selectinload(Conversation.rep),
            selectinload(Conversation.customer),
            selectinload(Conversation.messages),
        )
        .where(Conversation.id == conv.id)
    )
    conv_full = conv_full_result.scalar_one()
    await _handle_rep_reply(db, conv_full, msg_text)
    await db.commit()

    logger.info("Incoming WhatsApp from %s (%s) — conv %s", rep.name, sender_phone, conv.id)
    return {"status": "ok"}


# ── MANUAL SEND ───────────────────────────────────────────────────────────────
@router.post("/send", response_model=StatusResponse)
async def send_message(body: WhatsAppSendRequest, db: AsyncSession = Depends(get_db)):
    """
    Send a WhatsApp message. Called by the frontend when the user clicks
    'Send WhatsApp' on a draft message.
    Also marks the corresponding conversation message as sent.
    """
    try:
        result = await whatsapp_api.send_text(to=body.to, text=body.text)
        wa_msg_id = (result.get("messages") or [{}])[0].get("id", "")

        # Mark message sent if conversation_id provided
        if body.conversation_id and wa_msg_id:
            msg_result = await db.execute(
                select(Message)
                .where(
                    Message.conversation_id == body.conversation_id,
                    Message.status == "draft",
                    Message.text == body.text,
                )
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            msg = msg_result.scalar_one_or_none()
            if msg:
                msg.status = "sent"
                msg.is_read = True
                msg.whatsapp_msg_id = wa_msg_id
                await db.commit()

        return StatusResponse(status="sent", message=f"WhatsApp sent (id: {wa_msg_id})")
    except Exception as exc:
        logger.error("WhatsApp send error: %s", exc)
        raise HTTPException(500, str(exc))


# ── STATUS ────────────────────────────────────────────────────────────────────
@router.get("/status", response_model=StatusResponse)
async def whatsapp_status():
    configured = bool(settings.WHATSAPP_PHONE_NUMBER_ID and settings.WHATSAPP_ACCESS_TOKEN)
    return StatusResponse(
        status="connected" if configured else "not_configured",
        data={
            "phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID or "(not set)",
            "configured": configured,
        },
    )
