"""Dashboard stats and seed-data initialization route."""
from __future__ import annotations
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Conversation, Message, CRMComment
from app.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    # Conversation counts by handler — exclude check-in conversations
    convs_result = await db.execute(
        select(Conversation).where(
            (Conversation.crm_ref == None) |
            (~Conversation.crm_ref.like("checkin_%"))
        )
    )
    convs = convs_result.scalars().all()

    total = len(convs)
    escalated = sum(1 for c in convs if c.handler == "escalated")
    approval = sum(1 for c in convs if c.handler == "approval")
    senior = sum(1 for c in convs if c.handler == "senior")
    ai_auto = sum(1 for c in convs if c.handler == "ai")
    mukul_h = sum(1 for c in convs if c.handler == "mukul")

    # Message stats
    msgs_result = await db.execute(select(Message))
    msgs = msgs_result.scalars().all()

    nudges_sent = sum(1 for m in msgs if m.from_who == "mukul" and m.status == "sent")
    rep_replies = sum(1 for m in msgs if m.from_who == "rep")
    drafts = sum(1 for m in msgs if m.status == "draft")

    # CRM stats
    crm_result = await db.execute(select(CRMComment))
    crm_comments = crm_result.scalars().all()

    today = datetime.utcnow().date()
    crm_pending = sum(1 for c in crm_comments if c.resolution_status == "pending")
    crm_resolved_today = sum(
        1 for c in crm_comments
        if c.resolution_status == "resolved"
        and c.created_at.date() == today
    )

    return DashboardStats(
        total_conversations=total,
        escalated=escalated,
        approval_pending=approval,
        with_senior=senior,
        ai_autonomous=ai_auto,
        mukul_handling=mukul_h,
        nudges_sent=nudges_sent,
        rep_replies=rep_replies,
        drafts_pending=drafts,
        crm_comments_pending=crm_pending,
        crm_comments_resolved_today=crm_resolved_today,
    )
