"""
Conversation API routes — the core data layer for the inbox.

All actions that were previously inline JS (takeOver, resolveItem, etc.)
are now proper REST endpoints that persist to the database.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Conversation, Message, SeniorMessage, Rep, Customer, Senior
from app.schemas import (
    ConversationOut, ConversationCreate, ConversationUpdate,
    MessageCreate, MessageOut, SeniorMessageOut,
    GenerateNudgeResponse, StatusResponse,
)
from app.services import ai_brain, style_learner, escalation as esc_engine
from app.config import settings

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


# ── helpers ─────────────────────────────────────────────────────────────────
def _now_ts() -> str:
    return datetime.utcnow().strftime("%H:%M")


def _today_label() -> str:
    return "today"


async def _get_conv(conv_id: str, db: AsyncSession) -> Conversation:
    result = await db.execute(
        select(Conversation)
        .options(
            selectinload(Conversation.messages),
            selectinload(Conversation.senior_messages),
            selectinload(Conversation.rep),
            selectinload(Conversation.customer),
            selectinload(Conversation.senior_assigned),
        )
        .where(Conversation.id == conv_id)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


# ── LIST  ────────────────────────────────────────────────────────────────────
@router.get("", response_model=List[ConversationOut])
async def list_conversations(
    handler: Optional[str] = None,
    rep_type: Optional[str] = Query(None, description="Filter by rep type: sales, ccare, newbiz, admin, finance"),
    rep_id: Optional[str] = Query(None, description="Filter by specific rep ID"),
    source: Optional[str] = Query(None, description="Filter by source: checkin (visits) or comment (CRM comments)"),
    limit: int = Query(500, le=10000, description="Max conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    db: AsyncSession = Depends(get_db),
):
    q = select(Conversation).options(
        selectinload(Conversation.messages),
        selectinload(Conversation.senior_messages),
        selectinload(Conversation.rep),
        selectinload(Conversation.customer),
        selectinload(Conversation.senior_assigned),
    ).order_by(Conversation.updated_at.desc())

    if handler:
        q = q.where(Conversation.handler == handler)
    
    # Filter by specific rep
    if rep_id:
        q = q.where(Conversation.rep_id == rep_id)
    # Filter by rep type (only if rep_id not specified)
    elif rep_type:
        q = q.join(Rep).where(Rep.rep_type == rep_type)
    
    # Filter by conversation source
    if source == "checkin":
        # Check-in conversations have crm_ref like "checkin_%"
        q = q.where(Conversation.crm_ref.like("checkin_%"))
    elif source == "comment":
        # Comment-based conversations don't have "checkin_" prefix
        q = q.where(~Conversation.crm_ref.like("checkin_%") | (Conversation.crm_ref == None))

    # Add pagination
    q = q.limit(limit).offset(offset)

    result = await db.execute(q)
    return result.scalars().all()


# ── GET ONE ──────────────────────────────────────────────────────────────────
@router.get("/{conv_id}", response_model=ConversationOut)
async def get_conversation(conv_id: str, db: AsyncSession = Depends(get_db)):
    return await _get_conv(conv_id, db)


# ── CREATE ───────────────────────────────────────────────────────────────────
@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def create_conversation(body: ConversationCreate, db: AsyncSession = Depends(get_db)):
    conv = Conversation(
        id=str(uuid.uuid4()),
        **body.model_dump(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(conv)
    await db.commit()
    return await _get_conv(conv.id, db)


# ── UPDATE ───────────────────────────────────────────────────────────────────
@router.patch("/{conv_id}", response_model=ConversationOut)
async def update_conversation(
    conv_id: str, body: ConversationUpdate, db: AsyncSession = Depends(get_db)
):
    conv = await _get_conv(conv_id, db)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(conv, k, v)
    conv.updated_at = datetime.utcnow()
    await db.commit()
    return await _get_conv(conv_id, db)


# ── ADD MESSAGE ──────────────────────────────────────────────────────────────
@router.post("/{conv_id}/messages", response_model=MessageOut)
async def add_message(
    conv_id: str,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    conv = await _get_conv(conv_id, db)
    rep = conv.rep

    msg = Message(
        conversation_id=conv_id,
        from_who=body.from_who,
        text=body.text,
        ts=_now_ts(),
        date_label=_today_label(),
        status="received" if body.from_who == "rep" else "draft",
        is_read=body.from_who == "rep",
        by_ai=False,
        by_mukul_real=body.by_mukul_real,
        created_at=datetime.utcnow(),
    )
    db.add(msg)

    # Track real Mukul messages for style learning
    if body.from_who == "mukul" and body.by_mukul_real and rep:
        await style_learner.add_sample(
            db,
            text=body.text,
            source="real_message",
            rep_language=rep.language or "hinglish_80",
            context_type="nudge",
        )

    # If a rep reply came in, check CRM comments that were waiting
    if body.from_who == "rep":
        await _handle_rep_reply(db, conv, body.text)

    conv.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(msg)
    return msg


async def _handle_rep_reply(db: AsyncSession, conv: Conversation, reply_text: str):
    """
    When a rep replies, check if there's a pending CRM comment follow-up
    waiting for this reply. Score the reply and escalate if needed.
    """
    from app.models import CRMComment
    result = await db.execute(
        select(CRMComment)
        .where(
            CRMComment.conversation_id == conv.id,
            CRMComment.followup_sent == True,
            CRMComment.rep_reply == None,  # noqa: E711
        )
        .order_by(CRMComment.followup_sent_at.desc())
        .limit(1)
    )
    crm_comment = result.scalar_one_or_none()
    if not crm_comment or not crm_comment.followup_question:
        return

    # Score the reply
    score = await ai_brain.evaluate_confidence(
        question=crm_comment.followup_question,
        rep_reply=reply_text,
        context=crm_comment.processed_summary or "",
    )

    crm_comment.rep_reply = reply_text
    crm_comment.rep_reply_at = datetime.utcnow()
    crm_comment.confidence_score = score

    threshold = settings.AI_CONFIDENCE_THRESHOLD
    if score >= threshold:
        crm_comment.resolution_status = "resolved"
        conv.handler = "ai"
        conv.handler_reason = None
        conv.ai_confidence = score
    else:
        crm_comment.resolution_status = "escalated"
        should, target, reason = await esc_engine.should_escalate(score, conv, conv.rep)
        if should:
            if target == "senior" and conv.rep.reports_to_id:
                conv.handler = "senior"
                conv.senior_assigned_id = conv.rep.reports_to_id
            else:
                conv.handler = "escalated"
            conv.handler_reason = reason
        conv.ai_confidence = score


# ── GENERATE AI NUDGE ────────────────────────────────────────────────────────
@router.post("/{conv_id}/generate-nudge", response_model=GenerateNudgeResponse)
async def generate_nudge(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await _get_conv(conv_id, db)
    rep = conv.rep
    if not rep:
        raise HTTPException(400, "Rep not found")

    advisory = conv.handler == "mukul"
    text = await ai_brain.generate_nudge(
        db=db,
        conv=conv,
        rep=rep,
        customer=conv.customer,
        advisory_only=advisory,
    )

    if not advisory:
        # Determine if this message needs approval before sending
        needs_approval = esc_engine.should_require_approval(text, conv)
        msg = Message(
            conversation_id=conv_id,
            from_who="mukul",
            text=text,
            ts=_now_ts(),
            date_label=_today_label(),
            status="draft",
            is_read=False,
            by_ai=True,
            requires_approval=needs_approval,
            created_at=datetime.utcnow(),
        )
        db.add(msg)
        if needs_approval:
            conv.handler = "approval"
            conv.handler_reason = (
                "AI drafted a message that references Mukul's personal commitment "
                "or special pricing. Requires sign-off before sending."
            )
        conv.updated_at = datetime.utcnow()
        await db.commit()

    return GenerateNudgeResponse(text=text, advisory=advisory)


# ── MARK MESSAGE SENT ────────────────────────────────────────────────────────
@router.post("/{conv_id}/messages/{msg_id}/mark-sent", response_model=StatusResponse)
async def mark_message_sent(conv_id: str, msg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message).where(Message.id == msg_id, Message.conversation_id == conv_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Message not found")

    msg.status = "sent"
    msg.is_read = True
    msg.requires_approval = False

    conv = await _get_conv(conv_id, db)
    if conv.handler == "approval":
        conv.handler = "ai"
        conv.handler_reason = None

    # Store as approved AI sample for style learning
    if msg.by_ai and conv.rep:
        await style_learner.add_sample(
            db,
            text=msg.text,
            source="approved_ai",
            rep_language=conv.rep.language or "hinglish_80",
            context_type="nudge",
        )

    conv.updated_at = datetime.utcnow()
    await db.commit()
    return StatusResponse(status="ok", message="Message marked as sent")


# ── TAKE OVER ────────────────────────────────────────────────────────────────
@router.post("/{conv_id}/take-over", response_model=ConversationOut)
async def take_over(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await _get_conv(conv_id, db)
    conv.handler = "mukul"
    conv.handler_reason = "Mukul took over manually. AI on advisory standby."
    conv.senior_assigned_id = None
    conv.updated_at = datetime.utcnow()
    await db.commit()
    return await _get_conv(conv_id, db)


# ── RETURN TO AI ─────────────────────────────────────────────────────────────
@router.post("/{conv_id}/return-to-ai", response_model=ConversationOut)
async def return_to_ai(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await _get_conv(conv_id, db)
    conv.handler = "ai"
    conv.handler_reason = None
    conv.senior_assigned_id = None
    conv.updated_at = datetime.utcnow()
    await db.commit()
    return await _get_conv(conv_id, db)


# ── APPROVE DRAFT ────────────────────────────────────────────────────────────
@router.post("/{conv_id}/approve-draft", response_model=ConversationOut)
async def approve_draft(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await _get_conv(conv_id, db)
    # Remove requires_approval flag from last draft
    for msg in reversed(conv.messages):
        if msg.status == "draft":
            msg.requires_approval = False
            break
    conv.handler = "ai"
    conv.handler_reason = None
    conv.updated_at = datetime.utcnow()
    await db.commit()
    return await _get_conv(conv_id, db)


# ── FORWARD TO SENIOR ────────────────────────────────────────────────────────
@router.post("/{conv_id}/forward-to-senior/{senior_id}", response_model=ConversationOut)
async def forward_to_senior(
    conv_id: str, senior_id: str, db: AsyncSession = Depends(get_db)
):
    conv = await _get_conv(conv_id, db)

    s_result = await db.execute(select(Senior).where(Senior.id == senior_id))
    senior = s_result.scalar_one_or_none()
    if not senior:
        raise HTTPException(404, "Senior not found")

    conv.handler = "senior"
    conv.senior_assigned_id = senior_id
    conv.handler_reason = (
        f"Forwarded to {senior.name} ({senior.role}). "
        f"They have {settings.SENIOR_ESCALATION_WINDOW_HOURS}h to resolve before it bumps to Mukul."
    )
    conv.updated_at = datetime.utcnow()

    # Auto-generate briefing if no senior messages yet
    if not conv.senior_messages:
        try:
            briefing_text = await ai_brain.generate_senior_briefing(
                db=db, conv=conv, senior=senior,
                rep=conv.rep, customer=conv.customer,
            )
            briefing = SeniorMessage(
                conversation_id=conv_id,
                from_who="ai_to_senior",
                text=briefing_text,
                ts=_now_ts(),
                date_label=_today_label(),
                status="draft",
                is_read=False,
                created_at=datetime.utcnow(),
            )
            db.add(briefing)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("Briefing generation failed: %s", exc)

    await db.commit()
    return await _get_conv(conv_id, db)


# ── ESCALATE TO MUKUL ────────────────────────────────────────────────────────
@router.post("/{conv_id}/escalate-to-mukul", response_model=ConversationOut)
async def escalate_to_mukul(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await _get_conv(conv_id, db)
    conv.handler = "escalated"
    conv.senior_assigned_id = None
    conv.handler_reason = (
        (conv.handler_reason or "Senior could not resolve.") + " Bumped to Mukul for decision."
    )
    conv.updated_at = datetime.utcnow()
    await db.commit()
    return await _get_conv(conv_id, db)


# ── RESOLVE ──────────────────────────────────────────────────────────────────
@router.post("/{conv_id}/resolve", response_model=ConversationOut)
async def resolve_conversation(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await _get_conv(conv_id, db)
    conv.handler = "ai"
    conv.handler_reason = None
    conv.senior_assigned_id = None
    conv.is_resolved = False   # Stays active, just goes back to AI monitoring
    conv.updated_at = datetime.utcnow()
    await db.commit()
    return await _get_conv(conv_id, db)


# ── SENIOR THREAD ────────────────────────────────────────────────────────────
@router.post("/{conv_id}/senior-messages", response_model=SeniorMessageOut)
async def add_senior_message(
    conv_id: str,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a senior's reply to the senior thread."""
    await _get_conv(conv_id, db)  # validate exists
    msg = SeniorMessage(
        conversation_id=conv_id,
        from_who="senior",
        text=body.text,
        ts=_now_ts(),
        date_label=_today_label(),
        status="received",
        is_read=True,
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


@router.post("/{conv_id}/generate-senior-reply", response_model=GenerateNudgeResponse)
async def generate_senior_reply(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await _get_conv(conv_id, db)
    if not conv.senior_assigned_id:
        raise HTTPException(400, "No senior assigned to this conversation")

    s_result = await db.execute(select(Senior).where(Senior.id == conv.senior_assigned_id))
    senior = s_result.scalar_one_or_none()
    if not senior:
        raise HTTPException(404, "Senior not found")

    text = await ai_brain.generate_senior_reply(db=db, conv=conv, senior=senior, rep=conv.rep)

    msg = SeniorMessage(
        conversation_id=conv_id,
        from_who="ai_to_senior",
        text=text,
        ts=_now_ts(),
        date_label=_today_label(),
        status="draft",
        is_read=False,
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    conv.updated_at = datetime.utcnow()
    await db.commit()

    return GenerateNudgeResponse(text=text, advisory=False)


@router.post("/{conv_id}/senior-messages/{msg_id}/mark-sent", response_model=StatusResponse)
async def mark_senior_msg_sent(conv_id: str, msg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SeniorMessage).where(
            SeniorMessage.id == msg_id,
            SeniorMessage.conversation_id == conv_id,
        )
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Senior message not found")
    msg.status = "sent"
    msg.is_read = True
    await db.commit()
    return StatusResponse(status="ok")


# ── SEND NUDGE EMAIL ─────────────────────────────────────────────────────────
@router.post("/{conv_id}/send-email", response_model=StatusResponse)
async def send_nudge_email(
    conv_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Send the latest AI nudge (draft message) to the rep via email.
    Includes their original CRM field comment + Mukul's follow-up message.
    Reads as a direct message from Mukul — no AI mentions.
    """
    from app.services.email_service import send_nudge_email as _send
    from app.models import CRMComment

    conv = await _get_conv(conv_id, db)
    rep = conv.rep
    customer = conv.customer

    if not rep:
        raise HTTPException(400, "No rep linked to this conversation")
    if not rep.email:
        raise HTTPException(400, f"No email address on file for {rep.name}. Add it in Settings → Team.")

    # Get the latest draft/sent nudge from Mukul
    nudge_msg = None
    for m in reversed(conv.messages):
        if m.from_who == "mukul" and m.text:
            nudge_msg = m
            break

    if not nudge_msg:
        raise HTTPException(400, "No nudge message found in this conversation to send.")

    # Get the original CRM comment text if linked
    crm_comment_text = ""
    comment_date = ""
    if conv.crm_ref:
        crm_result = await db.execute(
            select(CRMComment).where(CRMComment.crm_comment_id == conv.crm_ref)
        )
        crm_comment = crm_result.scalar_one_or_none()
        if crm_comment:
            crm_comment_text = crm_comment.raw_text or ""
            comment_date = crm_comment.comment_date or ""

    # Fallback: use conversation intel/topic as context
    if not crm_comment_text:
        crm_comment_text = conv.intel or conv.objective or conv.topic or ""

    customer_name = customer.name if customer else conv.topic

    success = await _send(
        rep_email=rep.email,
        rep_name=rep.name,
        customer_name=customer_name,
        crm_comment=crm_comment_text,
        comment_date=comment_date,
        nudge_text=nudge_msg.text,
        mukul_name=settings.MUKUL_NAME,
    )

    if not success:
        raise HTTPException(500, "Failed to send email. Check SMTP settings in Settings page.")

    return StatusResponse(
        status="ok",
        message=f"Email sent to {rep.name} ({rep.email})",
        data={"rep_email": rep.email, "rep_name": rep.name},
    )


# ── Send WhatsApp nudge via AiSensy ──────────────────────────────────────────
class SendWhatsAppRequest(BaseModel):
    message_index: Optional[int] = None  # if None, sends the latest draft


@router.post("/{conv_id}/send-whatsapp", response_model=StatusResponse)
async def send_nudge_whatsapp(
    conv_id: str,
    body: SendWhatsAppRequest = SendWhatsAppRequest(),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a nudge message to the rep via WhatsApp (AiSensy API).
    Uses the CXNUDDGES campaign template.
    Marks the message as sent and stores the AiSensy message ID for tracking.
    """
    from app.services import aisensy_client

    conv = await _get_conv(conv_id, db)
    rep = conv.rep

    if not rep:
        raise HTTPException(400, "No rep linked to this conversation")
    if not rep.phone:
        raise HTTPException(400, f"No phone number on file for {rep.name}")

    # Find the message to send
    msg = None
    msg_db = None
    if body.message_index is not None:
        msgs = conv.messages
        if body.message_index < len(msgs):
            msg = msgs[body.message_index]
    else:
        # Find latest draft from mukul
        for m in reversed(conv.messages):
            if m.from_who == "mukul" and m.status == "draft":
                msg = m
                break

    if not msg:
        # Fall back to latest mukul message
        for m in reversed(conv.messages):
            if m.from_who == "mukul":
                msg = m
                break

    if not msg:
        raise HTTPException(400, "No message found to send")

    # Clean phone number — strip + and spaces
    phone = rep.phone.replace("+", "").replace(" ", "").strip()

    try:
        result = await aisensy_client.send_message(
            destination=phone,
            campaign_name="CXNUDDGES",
            template_params=[msg.text],
        )

        # Mark message as sent in DB
        msg.status = "sent"
        msg.is_read = True
        if hasattr(msg, 'whatsapp_msg_id'):
            msg.whatsapp_msg_id = result.get("submitted_message_id", "")
        await db.commit()

        return StatusResponse(
            status="ok",
            message=f"WhatsApp sent to {rep.name} ({phone})",
            data={
                "rep_name": rep.name,
                "phone": phone,
                "message_id": result.get("submitted_message_id", ""),
                "aisensy_response": result,
            },
        )

    except Exception as exc:
        raise HTTPException(500, f"WhatsApp send failed: {str(exc)}")
