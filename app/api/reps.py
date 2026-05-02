"""
Reps API - Get list of all reps for filtering
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models import Rep, Conversation

router = APIRouter(prefix="/api/reps", tags=["reps"])


class RepSummary(BaseModel):
    id: str
    name: str
    emp_code: str
    rep_type: str
    avatar: str
    color: str
    conversation_count: int
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[RepSummary])
async def list_reps(
    rep_type: Optional[str] = Query(None, description="Filter by rep type"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of all active reps with their conversation counts.
    Used for the rep selector dropdown.
    """
    query = (
        select(
            Rep.id,
            Rep.name,
            Rep.emp_code,
            Rep.rep_type,
            Rep.avatar,
            Rep.color,
            func.count(Conversation.id).label('conversation_count')
        )
        .outerjoin(Conversation, Conversation.rep_id == Rep.id)
        .where(Rep.is_active == True)
        .group_by(Rep.id, Rep.name, Rep.emp_code, Rep.rep_type, Rep.avatar, Rep.color)
        .order_by(Rep.name)
    )
    
    if rep_type:
        query = query.where(Rep.rep_type == rep_type)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        RepSummary(
            id=row.id,
            name=row.name,
            emp_code=row.emp_code,
            rep_type=row.rep_type,
            avatar=row.avatar,
            color=row.color,
            conversation_count=row.conversation_count
        )
        for row in rows
    ]


@router.get("/types")
async def get_rep_types(db: AsyncSession = Depends(get_db)):
    """
    Get summary of rep types with counts.
    """
    result = await db.execute(
        select(
            Rep.rep_type,
            func.count(Rep.id).label('rep_count'),
            func.count(Conversation.id).label('conversation_count')
        )
        .outerjoin(Conversation, Conversation.rep_id == Rep.id)
        .where(Rep.is_active == True)
        .group_by(Rep.rep_type)
        .order_by(Rep.rep_type)
    )
    
    rows = result.all()
    
    return {
        "types": [
            {
                "type": row.rep_type,
                "rep_count": row.rep_count,
                "conversation_count": row.conversation_count
            }
            for row in rows
        ]
    }
