"""
Rep Dashboard API - Different views for Sales, CCare, and NewBiz reps
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Rep, CheckIn, CRMComment, Conversation, Customer
from app.schemas import StatusResponse

router = APIRouter(prefix="/api/rep-dashboard", tags=["rep-dashboard"])


@router.get("/rep/{emp_code}")
async def get_rep_dashboard(
    emp_code: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard data for a specific rep based on their rep_type.
    
    - Sales reps: Check-ins, visits, comments
    - CCare/NewBiz reps: Comments, conversations, AI nudges
    """
    # Get rep details
    result = await db.execute(
        select(Rep).where(Rep.emp_code == emp_code)
    )
    rep = result.scalar_one_or_none()
    
    if not rep:
        return {"error": "Rep not found", "emp_code": emp_code}
    
    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime("%d-%m-%Y")
    
    dashboard_data = {
        "rep": {
            "emp_code": rep.emp_code,
            "name": rep.name,
            "role": rep.role,
            "rep_type": rep.rep_type,
            "phone": rep.phone,
            "region": rep.region,
        },
        "period": {
            "days": days,
            "from_date": from_date,
            "to_date": today.strftime("%d-%m-%Y"),
        }
    }
    
    # Get data based on rep_type
    if rep.rep_type == "sales":
        # Sales reps: Focus on check-ins and visits
        dashboard_data["data"] = await _get_sales_rep_data(db, emp_code, days, from_date)
    elif rep.rep_type in ["ccare", "newbiz"]:
        # CCare/NewBiz: Focus on comments and conversations
        dashboard_data["data"] = await _get_comment_based_rep_data(db, rep.id, emp_code, days)
    else:
        dashboard_data["data"] = {"message": "No specific dashboard for this rep type"}
    
    return dashboard_data


async def _get_sales_rep_data(db: AsyncSession, emp_code: str, days: int, from_date: str):
    """Get data for sales reps (check-ins focused)"""
    
    # Get check-ins
    result = await db.execute(
        select(CheckIn)
        .where(CheckIn.emp_code == emp_code)
        .where(CheckIn.checkin_date >= from_date)
        .order_by(CheckIn.checkin_date.desc(), CheckIn.checkin_time.desc())
    )
    checkins = result.scalars().all()
    
    # Calculate statistics
    total_visits = len(checkins)
    visits_with_comments = sum(1 for c in checkins if c.comment_id is not None)
    visits_without_comments = total_visits - visits_with_comments
    
    # Get unique customers visited
    unique_customers = len(set(c.comp_code for c in checkins if c.comp_code))
    
    # Group by date
    visits_by_date = {}
    for checkin in checkins:
        date = checkin.checkin_date
        if date not in visits_by_date:
            visits_by_date[date] = []
        visits_by_date[date].append({
            "id": checkin.id,
            "customer": checkin.comp_name or "Unknown",
            "comp_code": checkin.comp_code,
            "checkin_time": checkin.checkin_time,
            "checkout_time": checkin.checkout_time,
            "duration_minutes": checkin.duration_minutes,
            "address": checkin.address,
            "has_comment": checkin.comment_id is not None,
            "comment_id": checkin.comment_id,
            "latitude": checkin.latitude,
            "longitude": checkin.longitude,
        })
    
    # Get comments for this rep
    result = await db.execute(
        select(CRMComment)
        .where(CRMComment.crm_emp_code == emp_code)
        .order_by(CRMComment.created_at.desc())
        .limit(50)
    )
    comments = result.scalars().all()
    
    # Identify visits needing follow-up (no comment)
    needs_followup = []
    for checkin in checkins[:10]:  # Last 10 visits
        if not checkin.comment_id:
            needs_followup.append({
                "checkin_id": checkin.id,
                "customer": checkin.comp_name,
                "date": checkin.checkin_date,
                "time": checkin.checkin_time,
                "reason": "No comment added after visit"
            })
    
    return {
        "type": "sales",
        "summary": {
            "total_visits": total_visits,
            "unique_customers": unique_customers,
            "visits_with_comments": visits_with_comments,
            "visits_without_comments": visits_without_comments,
            "avg_visits_per_day": round(total_visits / days, 1) if days > 0 else 0,
        },
        "visits_by_date": visits_by_date,
        "needs_followup": needs_followup,
        "recent_comments": [
            {
                "id": c.id,
                "customer": c.customer.name if c.customer else "Unknown",
                "text": c.raw_text,
                "date": c.comment_date,
                "status": c.resolution_status,
            }
            for c in comments[:10]
        ]
    }


async def _get_comment_based_rep_data(db: AsyncSession, rep_id: str, emp_code: str, days: int):
    """Get data for CCare/NewBiz reps (comments and conversations focused)"""
    
    # Get comments
    result = await db.execute(
        select(CRMComment)
        .where(CRMComment.crm_emp_code == emp_code)
        .order_by(CRMComment.created_at.desc())
        .limit(100)
    )
    comments = result.scalars().all()
    
    # Get conversations
    result = await db.execute(
        select(Conversation)
        .where(Conversation.rep_id == rep_id)
        .order_by(Conversation.updated_at.desc())
        .limit(50)
    )
    conversations = result.scalars().all()
    
    # Calculate statistics
    total_comments = len(comments)
    pending_comments = sum(1 for c in comments if c.resolution_status == "pending")
    resolved_comments = sum(1 for c in comments if c.resolution_status == "resolved")
    escalated_comments = sum(1 for c in comments if c.resolution_status == "escalated")
    
    total_conversations = len(conversations)
    fresh_conversations = sum(1 for c in conversations if c.is_fresh)
    escalated_conversations = sum(1 for c in conversations if c.handler == "escalated")
    
    # Group comments by status
    comments_by_status = {
        "pending": [],
        "followup_sent": [],
        "resolved": [],
        "escalated": []
    }
    
    for comment in comments[:20]:  # Last 20 comments
        status = comment.resolution_status
        if status in comments_by_status:
            comments_by_status[status].append({
                "id": comment.id,
                "customer": comment.customer.name if comment.customer else "Unknown",
                "comp_code": comment.crm_comp_code,
                "text": comment.raw_text,
                "date": comment.comment_date,
                "followup_question": comment.followup_question,
                "rep_reply": comment.rep_reply,
                "confidence_score": comment.confidence_score,
                "conversation_id": comment.conversation_id,
            })
    
    # Get AI nudges (conversations with AI-generated messages)
    ai_nudges = []
    for conv in conversations[:10]:
        if conv.handler == "ai":
            ai_nudges.append({
                "id": conv.id,
                "customer": conv.customer.name if conv.customer else "Unknown",
                "topic": conv.topic,
                "urgency": conv.urgency,
                "confidence": conv.ai_confidence,
                "updated_at": conv.updated_at.isoformat(),
            })
    
    return {
        "type": "comment_based",
        "summary": {
            "total_comments": total_comments,
            "pending": pending_comments,
            "resolved": resolved_comments,
            "escalated": escalated_comments,
            "total_conversations": total_conversations,
            "fresh_conversations": fresh_conversations,
            "escalated_conversations": escalated_conversations,
        },
        "comments_by_status": comments_by_status,
        "ai_nudges": ai_nudges,
        "recent_conversations": [
            {
                "id": c.id,
                "customer": c.customer.name if c.customer else "Unknown",
                "topic": c.topic,
                "handler": c.handler,
                "urgency": c.urgency,
                "is_fresh": c.is_fresh,
                "updated_at": c.updated_at.isoformat(),
            }
            for c in conversations[:10]
        ]
    }


@router.get("/team/overview")
async def get_team_overview(
    rep_type: Optional[str] = Query(None, description="Filter by rep type: sales, ccare, newbiz"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get team overview with breakdown by rep type.
    """
    # Build query
    query = select(Rep).where(Rep.is_active == True)
    if rep_type:
        query = query.where(Rep.rep_type == rep_type)
    
    result = await db.execute(query)
    reps = result.scalars().all()
    
    # Group by rep_type
    reps_by_type = {}
    for rep in reps:
        if rep.rep_type not in reps_by_type:
            reps_by_type[rep.rep_type] = []
        reps_by_type[rep.rep_type].append({
            "emp_code": rep.emp_code,
            "name": rep.name,
            "role": rep.role,
            "region": rep.region,
        })
    
    # Get statistics
    today = datetime.now()
    from_date = (today - timedelta(days=days)).strftime("%d-%m-%Y")
    
    # Total check-ins (for sales reps)
    result = await db.execute(
        select(func.count(CheckIn.id))
        .where(CheckIn.checkin_date >= from_date)
    )
    total_checkins = result.scalar()
    
    # Total comments
    result = await db.execute(
        select(func.count(CRMComment.id))
    )
    total_comments = result.scalar()
    
    # Total conversations
    result = await db.execute(
        select(func.count(Conversation.id))
    )
    total_conversations = result.scalar()
    
    return {
        "period": {
            "days": days,
            "from_date": from_date,
            "to_date": today.strftime("%d-%m-%Y"),
        },
        "summary": {
            "total_reps": len(reps),
            "total_checkins": total_checkins,
            "total_comments": total_comments,
            "total_conversations": total_conversations,
        },
        "reps_by_type": reps_by_type,
        "type_counts": {
            rep_type: len(reps_list) 
            for rep_type, reps_list in reps_by_type.items()
        }
    }


@router.get("/checkin/{checkin_id}/comment")
async def get_checkin_comment(
    checkin_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the comment associated with a check-in (if any).
    """
    result = await db.execute(
        select(CheckIn).where(CheckIn.id == checkin_id)
    )
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        return {"error": "Check-in not found"}
    
    if not checkin.comment_id:
        return {
            "checkin": {
                "id": checkin.id,
                "customer": checkin.comp_name,
                "date": checkin.checkin_date,
                "time": checkin.checkin_time,
            },
            "comment": None,
            "message": "No comment linked to this check-in"
        }
    
    # Get the comment
    result = await db.execute(
        select(CRMComment).where(CRMComment.id == checkin.comment_id)
    )
    comment = result.scalar_one_or_none()
    
    return {
        "checkin": {
            "id": checkin.id,
            "customer": checkin.comp_name,
            "date": checkin.checkin_date,
            "time": checkin.checkin_time,
            "address": checkin.address,
        },
        "comment": {
            "id": comment.id,
            "text": comment.raw_text,
            "date": comment.comment_date,
            "status": comment.resolution_status,
            "followup_question": comment.followup_question,
            "rep_reply": comment.rep_reply,
            "confidence_score": comment.confidence_score,
        } if comment else None
    }
