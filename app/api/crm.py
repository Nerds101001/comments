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
    """Get the last CRM sync time, pending comments count, and check-in stats."""
    from app.models import AppSetting, CheckIn
    
    # Get last sync time for comments
    last_sync_result = await db.execute(
        select(AppSetting).where(AppSetting.key == "last_crm_sync")
    )
    last_sync_setting = last_sync_result.scalar_one_or_none()
    last_sync = last_sync_setting.value if last_sync_setting else None
    
    # Get last sync time for check-ins
    last_checkin_sync_result = await db.execute(
        select(AppSetting).where(AppSetting.key == "last_checkin_sync")
    )
    last_checkin_sync_setting = last_checkin_sync_result.scalar_one_or_none()
    last_checkin_sync = last_checkin_sync_setting.value if last_checkin_sync_setting else None
    
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
    
    # Count total check-ins
    checkin_result = await db.execute(select(CheckIn))
    total_checkins = len(checkin_result.scalars().all())
    
    # Count new comments since last sync
    new_comments_count = 0
    if last_sync:
        try:
            last_sync_dt = datetime.fromisoformat(last_sync.replace("Z", "").replace("+00:00", ""))
            new_comments_result = await db.execute(
                select(CRMComment).where(CRMComment.created_at >= last_sync_dt)
            )
            new_comments_count = len(new_comments_result.scalars().all())
        except Exception:
            pass
    
    # Count new check-ins since last sync
    new_checkins_count = 0
    if last_checkin_sync:
        try:
            last_checkin_sync_dt = datetime.fromisoformat(last_checkin_sync.replace("Z", "").replace("+00:00", ""))
            new_checkins_result = await db.execute(
                select(CheckIn).where(CheckIn.created_at >= last_checkin_sync_dt)
            )
            new_checkins_count = len(new_checkins_result.scalars().all())
        except Exception:
            pass
    
    return StatusResponse(
        status="ok",
        data={
            "last_sync": last_sync,
            "last_checkin_sync": last_checkin_sync,
            "pending_count": pending_count,
            "processed_count": processed_count,
            "total_count": total_count,
            "total_checkins": total_checkins,
            "new_comments_since_last_sync": new_comments_count,
            "new_checkins_since_last_sync": new_checkins_count,
        },
    )


# ── SYNC  (fetch fresh comments from CRM) ────────────────────────────────────
@router.post("/sync", response_model=StatusResponse)
async def sync_crm_comments(
    hours_back: Optional[int] = Query(None, description="Hours back for date-range sync"),
    days_back: Optional[int] = Query(None, description="Days back for date-range sync (overrides hours_back)"),
    emp_code: Optional[str] = Query(None, description="Override: limit to one specific rep's emp_code"),
    db: AsyncSession = Depends(get_db),
):
    """
    Pull comments from the CRM using GetCommentsReport via admin account
    (Nagender, emp_code=1494) — ONE single call returns all reps' comments
    for the given date range.

    Default (no params): last 48 hours.
    days_back=30  → last 30 days (manual sync)
    days_back=182 → last 6 months (deep sync)

    Already-processed records are skipped automatically via deduplication
    (COMMENT_ID match), so re-syncing overlapping date ranges is safe.
    """
    from datetime import timedelta
    from app.models import AppSetting

    today = datetime.utcnow()
    admin_emp = settings.CRM_ADMIN_EMP_CODE  # "1494" — Nagender

    # Determine date range — plain int values when called internally, Query when via HTTP
    _days_back  = int(days_back)  if days_back  is not None else None
    _hours_back = int(hours_back) if hours_back is not None else None

    if _days_back is not None:
        delta_days = _days_back
    elif _hours_back is not None:
        delta_days = max(1, (_hours_back + 23) // 24)  # round up to full days
    else:
        delta_days = 2  # default: last 48 hours

    from_date_str = (today - timedelta(days=delta_days)).strftime("%Y-%m-%d")
    to_date_str   = today.strftime("%Y-%m-%d")
    target_emp    = emp_code or admin_emp

    logger.info("CRM comment sync via GetCommentsReport: emp=%s %s → %s (%d days)",
                target_emp, from_date_str, to_date_str, delta_days)

    # Load customers and reps for lookup
    custs_result = await db.execute(select(Customer))
    custs_by_code: dict[str, Customer] = {c.comp_code: c for c in custs_result.scalars().all()}

    reps_result = await db.execute(select(Rep))
    reps_by_emp: dict[str, Rep] = {r.emp_code: r for r in reps_result.scalars().all()}

    # ONE admin call — returns all reps' comments for the date range
    raw_comments = await crm_client.get_comments_report(
        from_date=from_date_str,
        to_date=to_date_str,
        emp_code=target_emp,
    )
    logger.info("GetCommentsReport returned %d records", len(raw_comments))

    new_count = 0

    for raw in raw_comments:
        # Skip rows with no actual comment text
        comment_text = str(raw.get("COMMENT") or "").strip()
        if not comment_text:
            continue

        crm_id      = str(raw.get("COMMENT_ID") or "")
        comp_code   = str(raw.get("COMP_CODE") or "")
        crm_emp_code = str(raw.get("EMP_CODE") or "")
        comment_date = str(raw.get("CREATEDON") or "")

        # Dedup by COMMENT_ID (skip if 0 or empty — use fallback)
        if crm_id and crm_id != "0":
            exists = await db.execute(
                select(CRMComment).where(CRMComment.crm_comment_id == crm_id)
            )
            if exists.scalar_one_or_none():
                continue
        else:
            # Fallback dedup: emp + comp + date + text prefix
            if comment_text and crm_emp_code and comment_date:
                exists2 = await db.execute(
                    select(CRMComment).where(
                        CRMComment.crm_emp_code == crm_emp_code,
                        CRMComment.crm_comp_code == (comp_code or None),
                        CRMComment.comment_date == comment_date,
                        CRMComment.raw_text.startswith(comment_text[:80]),
                    )
                )
                if exists2.scalar_one_or_none():
                    continue

        customer = custs_by_code.get(comp_code)
        rep      = reps_by_emp.get(crm_emp_code)

        db.add(CRMComment(
            crm_comment_id=crm_id if crm_id and crm_id != "0" else None,
            rep_id=rep.id if rep else None,
            customer_id=customer.id if customer else None,
            crm_emp_code=crm_emp_code,
            crm_comp_code=comp_code or None,
            raw_text=comment_text,
            comment_date=comment_date,
            resolution_status="pending",
            created_at=datetime.utcnow(),
        ))
        new_count += 1

    await db.commit()

    # Update last sync timestamp
    last_sync_result = await db.execute(
        select(AppSetting).where(AppSetting.key == "last_crm_sync")
    )
    last_sync_setting = last_sync_result.scalar_one_or_none()
    now_iso = today.isoformat()
    if last_sync_setting:
        last_sync_setting.value = now_iso
        last_sync_setting.updated_at = today
    else:
        db.add(AppSetting(key="last_crm_sync", value=now_iso, updated_at=today))
    await db.commit()

    logger.info("CRM sync complete: %d new comments from %d CRM records (admin emp=%s)",
                new_count, len(raw_comments), admin_emp)
    return StatusResponse(
        status="ok",
        message=f"Synced {new_count} new comments",
        data={
            "new_comments": new_count,
            "crm_records_fetched": len(raw_comments),
            "last_sync": now_iso,
            "from_date": from_date_str,
            "to_date": to_date_str,
            "admin_emp_code": admin_emp,
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
