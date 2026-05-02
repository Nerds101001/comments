"""
CRM integration routes.

The main AI loop:
  1. POST /api/crm/sync         — pull fresh comments from rustx CRM
  2. GET  /api/crm/comments     — list locally stored CRM comments
  3. POST /api/crm/comments/{id}/process  — AI processes one comment
  4. POST /api/crm/process-all  — batch process all pending comments
  5. GET  /api/crm/status       — connection health

After a comment is processed, the AI:
  - Generates a follow-up WhatsApp question for the rep
  - Sends it (if WhatsApp configured)
  - When the rep replies (via webhook), scores confidence
  - If >= 88% → resolves; else → escalates to senior/Mukul
"""
from __future__ import annotations
import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Conversation, CRMComment, Message, Rep, Customer
from app.schemas import CRMCommentOut, StatusResponse
from app.services import ai_brain, crm_client, whatsapp_api, escalation as esc_engine
from app.config import settings

router = APIRouter(prefix="/api/crm", tags=["crm"])
logger = logging.getLogger(__name__)


def _now_ts() -> str:
    return datetime.utcnow().strftime("%H:%M")


# ── CRM STATUS ────────────────────────────────────────────────────────────────
@router.get("/status", response_model=StatusResponse)
async def crm_status():
    result = await crm_client.test_connection()
    return StatusResponse(
        status="connected" if result["connected"] else "error",
        data=result,
    )


# ── SYNC STATUS ───────────────────────────────────────────────────────────────
@router.get("/sync-status", response_model=StatusResponse)
async def get_sync_status(db: AsyncSession = Depends(get_db)):
    """Get the last CRM sync time and pending comments count."""
    from app.models import AppSetting
    
    # Get last sync time
    last_sync_result = await db.execute(
        select(AppSetting).where(AppSetting.key == "last_crm_sync")
    )
    last_sync_setting = last_sync_result.scalar_one_or_none()
    last_sync = last_sync_setting.value if last_sync_setting else None
    
    # Count pending comments
    pending_result = await db.execute(
        select(CRMComment).where(CRMComment.resolution_status == "pending")
    )
    pending_count = len(pending_result.scalars().all())
    
    # Count total comments
    total_result = await db.execute(select(CRMComment))
    total_count = len(total_result.scalars().all())
    
    # Count processed comments
    processed_result = await db.execute(
        select(CRMComment).where(CRMComment.resolution_status != "pending")
    )
    processed_count = len(processed_result.scalars().all())
    
    return StatusResponse(
        status="ok",
        data={
            "last_sync": last_sync,
            "pending_count": pending_count,
            "processed_count": processed_count,
            "total_count": total_count,
        },
    )


# ── SYNC  (fetch fresh comments from CRM) ────────────────────────────────────
@router.post("/sync", response_model=StatusResponse)
async def sync_crm_comments(
    hours_back: Optional[int] = Query(None, description="How many hours back to fetch (default: since last sync)"),
    emp_code: Optional[str] = Query(None, description="Limit to one rep's emp_code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Pull comments from the CRM and store new ones locally.
    Uses GetCustomersLastComment (per rep) + GetPipelineComment (date range).
    
    Incremental sync: If hours_back is not specified, fetches only new comments since last sync.
    """
    from datetime import timedelta
    from app.models import AppSetting
    
    today = datetime.utcnow()
    
    # Check last sync time for incremental sync
    if hours_back is None:
        last_sync_result = await db.execute(
            select(AppSetting).where(AppSetting.key == "last_crm_sync")
        )
        last_sync_setting = last_sync_result.scalar_one_or_none()
        
        if last_sync_setting:
            try:
                last_sync_time = datetime.fromisoformat(last_sync_setting.value)
                hours_back = int((today - last_sync_time).total_seconds() / 3600) + 1
                logger.info(f"Incremental sync: fetching last {hours_back} hours since {last_sync_time}")
            except:
                hours_back = 1  # Default to 1 hour if parsing fails
        else:
            hours_back = 1  # First sync, fetch last hour
    
    from_dt = today - timedelta(hours=hours_back)
    from_date = from_dt.strftime("%d-%m-%Y")
    to_date = today.strftime("%d-%m-%Y")

    # Load all reps to map emp_code → rep.id
    reps_result = await db.execute(select(Rep))
    all_reps = reps_result.scalars().all()
    reps_by_emp: dict[str, Rep] = {r.emp_code: r for r in all_reps}

    # Load all customers to map comp_code → customer
    custs_result = await db.execute(select(Customer))
    all_custs = custs_result.scalars().all()
    custs_by_code: dict[str, Customer] = {c.comp_code: c for c in all_custs}

    target_reps = [r for r in all_reps if not emp_code or r.emp_code == emp_code]
    new_count = 0

    for rep in target_reps:
        comments = await crm_client.get_pipeline_comments(
            emp_code=rep.emp_code,
            from_date=from_date,
            to_date=to_date,
        )
        for raw in comments:
            crm_id = str(raw.get("id") or raw.get("commentId") or raw.get("CommentId", ""))

            # Skip if already stored
            if crm_id:
                exists_result = await db.execute(
                    select(CRMComment).where(CRMComment.crm_comment_id == crm_id)
                )
                if exists_result.scalar_one_or_none():
                    continue

            comment_text = (
                raw.get("comment") or raw.get("Comment") or
                raw.get("remarks") or raw.get("Remarks") or str(raw)
            )
            comp_code = str(raw.get("compCode") or raw.get("CompCode") or "")
            crm_emp_code = str(raw.get("empCode") or raw.get("EmpCode") or rep.emp_code)
            comment_date = str(raw.get("date") or raw.get("Date") or raw.get("createdOn") or "")

            customer = custs_by_code.get(comp_code)

            c = CRMComment(
                crm_comment_id=crm_id or None,
                rep_id=rep.id,
                customer_id=customer.id if customer else None,
                crm_emp_code=crm_emp_code,
                crm_comp_code=comp_code or None,
                raw_text=comment_text,
                comment_date=comment_date,
                resolution_status="pending",
                created_at=datetime.utcnow(),
            )
            db.add(c)
            new_count += 1

    await db.commit()
    
    # Update last sync time
    from app.models import AppSetting
    last_sync_result = await db.execute(
        select(AppSetting).where(AppSetting.key == "last_crm_sync")
    )
    last_sync_setting = last_sync_result.scalar_one_or_none()
    
    if last_sync_setting:
        last_sync_setting.value = today.isoformat()
        last_sync_setting.updated_at = today
    else:
        last_sync_setting = AppSetting(
            key="last_crm_sync",
            value=today.isoformat(),
            updated_at=today
        )
        db.add(last_sync_setting)
    
    await db.commit()
    
    logger.info("CRM sync: fetched %d new comments", new_count)
    return StatusResponse(
        status="ok",
        message=f"Synced {new_count} new comments",
        data={
            "new_comments": new_count,
            "last_sync": today.isoformat(),
            "hours_back": hours_back
        },
    )


# ── LIST COMMENTS ─────────────────────────────────────────────────────────────
@router.get("/comments", response_model=List[CRMCommentOut])
async def list_comments(
    status: Optional[str] = Query(None, description="pending|followup_sent|resolved|escalated"),
    rep_id: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(CRMComment).order_by(CRMComment.created_at.desc()).limit(limit)
    if status:
        q = q.where(CRMComment.resolution_status == status)
    if rep_id:
        q = q.where(CRMComment.rep_id == rep_id)
    result = await db.execute(q)
    return result.scalars().all()


# ── PROCESS ONE COMMENT ───────────────────────────────────────────────────────
@router.post("/comments/{comment_id}/process", response_model=CRMCommentOut)
async def process_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    """
    AI processes a single CRM comment:
    1. Summarise the visit/note
    2. Generate a follow-up question
    3. Create/link a Conversation in the inbox
    4. Send the follow-up via WhatsApp (if configured)
    """
    c_result = await db.execute(
        select(CRMComment)
        .options(selectinload(CRMComment.rep), selectinload(CRMComment.customer))
        .where(CRMComment.id == comment_id)
    )
    comment = c_result.scalar_one_or_none()
    if not comment:
        raise HTTPException(404, "Comment not found")

    rep = comment.rep
    customer = comment.customer

    # AI processing
    result = await ai_brain.process_crm_comment(
        raw_comment=comment.raw_text,
        rep=rep,
        customer=customer,
    )

    comment.processed_summary = result.get("summary", "")
    comment.followup_question = result.get("followup_question")
    urgency = result.get("urgency", "medium")

    if result.get("needs_followup") and comment.followup_question:
        # Create or link a Conversation
        if not comment.conversation_id:
            conv_topic = (
                f"CRM: {customer.name}" if customer
                else f"CRM comment — {rep.name}"
            )
            conv = Conversation(
                id=str(uuid.uuid4()),
                rep_id=rep.id,
                customer_id=customer.id if customer else None,
                topic=conv_topic,
                pipeline_stage=result.get("stage", "Field visit follow-up"),
                objective=comment.followup_question,
                tactic="CRM-driven follow-up",
                intel=comment.processed_summary,
                urgency=urgency,
                handler="ai",
                crm_ref=comment.crm_comment_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(conv)
            await db.flush()  # get conv.id

            # Add the follow-up question as a Mukul draft message
            msg = Message(
                conversation_id=conv.id,
                from_who="mukul",
                text=comment.followup_question,
                ts=_now_ts(),
                date_label="today",
                status="draft",
                is_read=False,
                by_ai=True,
                created_at=datetime.utcnow(),
            )
            db.add(msg)
            comment.conversation_id = conv.id

        # Send via WhatsApp
        if settings.WHATSAPP_PHONE_NUMBER_ID and rep.phone:
            try:
                await whatsapp_api.send_text(to=rep.phone, text=comment.followup_question)
                comment.followup_sent = True
                comment.followup_sent_at = datetime.utcnow()
                comment.resolution_status = "followup_sent"
                # Mark message as sent
                if comment.conversation_id:
                    msg_result = await db.execute(
                        select(Message).where(
                            Message.conversation_id == comment.conversation_id,
                            Message.status == "draft",
                        ).order_by(Message.created_at.desc()).limit(1)
                    )
                    draft_msg = msg_result.scalar_one_or_none()
                    if draft_msg:
                        draft_msg.status = "sent"
                        draft_msg.is_read = True
            except Exception as exc:
                logger.warning("Could not send WhatsApp follow-up: %s", exc)
    else:
        comment.resolution_status = "resolved"

    await db.commit()
    await db.refresh(comment)
    return comment


# ── PROCESS ALL PENDING ───────────────────────────────────────────────────────
@router.post("/process-all", response_model=StatusResponse)
async def process_all_pending(db: AsyncSession = Depends(get_db)):
    """Batch-process all pending CRM comments. Good to call after a sync."""
    result = await db.execute(
        select(CRMComment)
        .where(CRMComment.resolution_status == "pending")
        .order_by(CRMComment.created_at.asc())
        .limit(50)
    )
    pending = result.scalars().all()
    processed = 0
    errors = 0

    for comment in pending:
        try:
            # Re-load with relationships for each
            c_full = await db.execute(
                select(CRMComment)
                .options(selectinload(CRMComment.rep), selectinload(CRMComment.customer))
                .where(CRMComment.id == comment.id)
            )
            c = c_full.scalar_one()
            # Use the process_comment logic directly
            from fastapi import Request  # minimal reuse
            from app.api.crm import process_comment as _process
            await process_comment(c.id, db)
            processed += 1
        except Exception as exc:
            logger.error("Error processing comment %d: %s", comment.id, exc)
            errors += 1

    return StatusResponse(
        status="ok",
        message=f"Processed {processed} comments ({errors} errors)",
        data={"processed": processed, "errors": errors},
    )
