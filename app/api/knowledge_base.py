"""
AI Knowledge Base API endpoints.
Allows users to manage training data for AI nudge generation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import AIKnowledgeBase

router = APIRouter(prefix="/api/knowledge", tags=["AI Knowledge Base"])


# ─────────────────────────────────────────────────────────
#  SCHEMAS
# ─────────────────────────────────────────────────────────
class KnowledgeBaseCreate(BaseModel):
    category: str  # example_nudge, product_info, terminology, guideline
    title: str
    content: str
    language: str = "all"
    priority: int = 5
    created_by: Optional[str] = None


class KnowledgeBaseUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    category: str
    title: str
    content: str
    language: str
    priority: int
    is_active: bool
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────
#  ENDPOINTS
# ─────────────────────────────────────────────────────────
@router.get("/entries", response_model=List[KnowledgeBaseResponse])
async def get_knowledge_entries(
    category: Optional[str] = None,
    language: Optional[str] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Get all knowledge base entries with optional filtering."""
    query = select(AIKnowledgeBase)
    
    if category:
        query = query.where(AIKnowledgeBase.category == category)
    if language:
        query = query.where(
            (AIKnowledgeBase.language == language) | (AIKnowledgeBase.language == "all")
        )
    if active_only:
        query = query.where(AIKnowledgeBase.is_active == True)
    
    query = query.order_by(AIKnowledgeBase.priority.desc(), AIKnowledgeBase.created_at.desc())
    
    result = await db.execute(query)
    entries = result.scalars().all()
    return entries


@router.get("/entries/{entry_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single knowledge base entry by ID."""
    result = await db.execute(
        select(AIKnowledgeBase).where(AIKnowledgeBase.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    return entry


@router.post("/entries", response_model=KnowledgeBaseResponse)
async def create_knowledge_entry(
    data: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new knowledge base entry."""
    entry = AIKnowledgeBase(
        category=data.category,
        title=data.title,
        content=data.content,
        language=data.language,
        priority=data.priority,
        created_by=data.created_by,
    )
    
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    return entry


@router.put("/entries/{entry_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_entry(
    entry_id: int,
    data: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing knowledge base entry."""
    result = await db.execute(
        select(AIKnowledgeBase).where(AIKnowledgeBase.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    # Update fields
    if data.category is not None:
        entry.category = data.category
    if data.title is not None:
        entry.title = data.title
    if data.content is not None:
        entry.content = data.content
    if data.language is not None:
        entry.language = data.language
    if data.priority is not None:
        entry.priority = data.priority
    if data.is_active is not None:
        entry.is_active = data.is_active
    
    entry.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(entry)
    
    return entry


@router.delete("/entries/{entry_id}")
async def delete_knowledge_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a knowledge base entry."""
    result = await db.execute(
        select(AIKnowledgeBase).where(AIKnowledgeBase.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    
    await db.delete(entry)
    await db.commit()
    
    return {"success": True, "message": "Knowledge entry deleted"}


@router.get("/stats")
async def get_knowledge_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics about the knowledge base."""
    # Total entries
    total_result = await db.execute(select(func.count(AIKnowledgeBase.id)))
    total = total_result.scalar()
    
    # Active entries
    active_result = await db.execute(
        select(func.count(AIKnowledgeBase.id)).where(AIKnowledgeBase.is_active == True)
    )
    active = active_result.scalar()
    
    # By category
    category_result = await db.execute(
        select(AIKnowledgeBase.category, func.count(AIKnowledgeBase.id))
        .where(AIKnowledgeBase.is_active == True)
        .group_by(AIKnowledgeBase.category)
    )
    by_category = {cat: count for cat, count in category_result.all()}
    
    return {
        "total_entries": total,
        "active_entries": active,
        "inactive_entries": total - active,
        "by_category": by_category,
    }
