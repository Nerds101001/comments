"""
SQLAlchemy ORM models for Hi-Tech AI Sales Org.
All tables use async SQLite via aiosqlite.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Boolean, Text, DateTime, JSON,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


# ─────────────────────────────────────────────────────────
#  SENIOR LAYER
# ─────────────────────────────────────────────────────────
class Senior(Base):
    __tablename__ = "seniors"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)          # e.g. 'anthony'
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(100), default="Senior Sales Manager")
    phone: Mapped[str] = mapped_column(String(20))                          # WhatsApp number
    avatar: Mapped[str] = mapped_column(String(5))
    color: Mapped[str] = mapped_column(String(12), default="#5856D6")
    region: Mapped[str] = mapped_column(String(100), default="")
    language: Mapped[str] = mapped_column(String(30), default="english_only")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    reps: Mapped[List["Rep"]] = relationship("Rep", back_populates="senior")
    escalated_convs: Mapped[List["Conversation"]] = relationship(
        "Conversation", foreign_keys="Conversation.senior_assigned_id",
        back_populates="senior_assigned"
    )


# ─────────────────────────────────────────────────────────
#  SALES REP (TEAM MEMBER)
# ─────────────────────────────────────────────────────────
class Rep(Base):
    __tablename__ = "reps"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)           # e.g. 'r1'
    name: Mapped[str] = mapped_column(String(100))
    emp_code: Mapped[str] = mapped_column(String(20))
    phone: Mapped[str] = mapped_column(String(20))                          # WhatsApp
    region: Mapped[str] = mapped_column(String(100), default="")
    avatar: Mapped[str] = mapped_column(String(5))
    color: Mapped[str] = mapped_column(String(12), default="#007AFF")
    intensity: Mapped[str] = mapped_column(String(20), default="standard")  # high/standard/light/minimal
    language: Mapped[str] = mapped_column(String(30), default="hinglish_80")
    role: Mapped[str] = mapped_column(String(80), default="Sales Person")
    rep_type: Mapped[str] = mapped_column(String(20), default="sales")      # sales/ccare/newbiz/admin/finance
    reports_to_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("seniors.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Rep's email address

    senior: Mapped[Optional["Senior"]] = relationship("Senior", back_populates="reps")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="rep")


# ─────────────────────────────────────────────────────────
#  CUSTOMER / COMPANY
# ─────────────────────────────────────────────────────────
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)           # e.g. 'cu1'
    comp_code: Mapped[str] = mapped_column(String(30), index=True)          # CRM comp code
    name: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100), default="")
    state: Mapped[str] = mapped_column(String(100), default="")
    cust_type: Mapped[str] = mapped_column(String(20), default="new")       # regular/new/at_risk/dormant
    last_order_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    products_bought: Mapped[list] = mapped_column(JSON, default=list)
    ltv: Mapped[str] = mapped_column(String(50), default="unknown")
    cross_sell: Mapped[list] = mapped_column(JSON, default=list)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="customer")
    crm_comments: Mapped[List["CRMComment"]] = relationship("CRMComment", back_populates="customer")


# ─────────────────────────────────────────────────────────
#  CONVERSATION
# ─────────────────────────────────────────────────────────
class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    rep_id: Mapped[str] = mapped_column(String(20), ForeignKey("reps.id"), index=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("customers.id"), nullable=True)
    topic: Mapped[str] = mapped_column(String(300))
    pipeline_stage: Mapped[str] = mapped_column(String(200), default="")
    objective: Mapped[str] = mapped_column(String(300), default="")
    tactic: Mapped[str] = mapped_column(String(300), default="")
    intel: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    urgency: Mapped[str] = mapped_column(String(20), default="medium")      # high/medium/low
    # Handler: ai | escalated | approval | senior | mukul
    handler: Mapped[str] = mapped_column(String(20), default="ai")
    handler_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    senior_assigned_id: Mapped[Optional[str]] = mapped_column(
        String(20), ForeignKey("seniors.id"), nullable=True
    )
    ai_confidence: Mapped[int] = mapped_column(Integer, default=75)
    is_fresh: Mapped[bool] = mapped_column(Boolean, default=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    crm_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # CRM comment id
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rep: Mapped["Rep"] = relationship("Rep", back_populates="conversations")
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="conversations")
    senior_assigned: Mapped[Optional["Senior"]] = relationship(
        "Senior", foreign_keys=[senior_assigned_id], back_populates="escalated_convs"
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation",
        order_by="Message.created_at", cascade="all, delete-orphan"
    )
    senior_messages: Mapped[List["SeniorMessage"]] = relationship(
        "SeniorMessage", back_populates="conversation",
        order_by="SeniorMessage.created_at", cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────────────────
#  MESSAGE  (Mukul ↔ Rep thread)
# ─────────────────────────────────────────────────────────
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(String(40), ForeignKey("conversations.id"), index=True)
    from_who: Mapped[str] = mapped_column(String(10))                       # 'mukul' | 'rep'
    text: Mapped[str] = mapped_column(Text)
    ts: Mapped[str] = mapped_column(String(10))                             # HH:MM display time
    date_label: Mapped[str] = mapped_column(String(20), default="today")    # today/yesterday
    status: Mapped[str] = mapped_column(String(20), default="draft")        # draft/sent/received
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    by_ai: Mapped[bool] = mapped_column(Boolean, default=False)
    by_mukul_real: Mapped[bool] = mapped_column(Boolean, default=False)     # Real (not AI) Mukul msg
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    whatsapp_msg_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")


# ─────────────────────────────────────────────────────────
#  SENIOR MESSAGE  (Mukul ↔ Senior thread)
# ─────────────────────────────────────────────────────────
class SeniorMessage(Base):
    __tablename__ = "senior_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(String(40), ForeignKey("conversations.id"), index=True)
    from_who: Mapped[str] = mapped_column(String(20))                       # 'ai_to_senior' | 'senior'
    text: Mapped[str] = mapped_column(Text)
    ts: Mapped[str] = mapped_column(String(10))
    date_label: Mapped[str] = mapped_column(String(20), default="today")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="senior_messages")


# ─────────────────────────────────────────────────────────
#  STYLE SAMPLE  (adaptive writing style learning)
# ─────────────────────────────────────────────────────────
class StyleSample(Base):
    """Every real Mukul message + approved AI messages feed the style learner."""
    __tablename__ = "style_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(30))                         # real_message | edited_ai | gmail | approved_ai
    text: Mapped[str] = mapped_column(Text)
    rep_language: Mapped[str] = mapped_column(String(30), default="hinglish_80")
    context_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # nudge/followup/escalation
    approved: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────────────────
#  STYLE PROFILE  (distilled style summary per language)
# ─────────────────────────────────────────────────────────
class StyleProfile(Base):
    """AI-generated style summary, refreshed whenever enough new samples accumulate."""
    __tablename__ = "style_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    language_key: Mapped[str] = mapped_column(String(30), unique=True)
    summary: Mapped[str] = mapped_column(Text)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────────────────
#  CRM COMMENT  (fetched from rustx CRM)
# ─────────────────────────────────────────────────────────
class CRMComment(Base):
    """
    Each comment/visit note fetched from the CRM.
    Flow: fetched → AI processes → followup_question sent to rep
          → rep replies → confidence scored → resolved or escalated
    """
    __tablename__ = "crm_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crm_comment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    rep_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("reps.id"), nullable=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("customers.id"), nullable=True)
    crm_emp_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)   # emp code from CRM
    crm_comp_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # comp code from CRM
    raw_text: Mapped[str] = mapped_column(Text)
    comment_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    processed_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    followup_question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    followup_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    followup_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rep_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rep_reply_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    confidence_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # pending | followup_sent | resolved | escalated
    resolution_status: Mapped[str] = mapped_column(String(20), default="pending")
    conversation_id: Mapped[Optional[str]] = mapped_column(
        String(40), ForeignKey("conversations.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rep: Mapped[Optional["Rep"]] = relationship("Rep")
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="crm_comments")


# ─────────────────────────────────────────────────────────
#  APP SETTING  (key-value store for runtime config)
# ─────────────────────────────────────────────────────────
class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)                                # JSON-serialised
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─────────────────────────────────────────────────────────
#  AI KNOWLEDGE BASE  (training data for personalized nudges)
# ─────────────────────────────────────────────────────────
class AIKnowledgeBase(Base):
    """
    Knowledge base entries that train the AI on how to write nudges.
    Users can add examples of good nudges, company-specific terminology,
    product knowledge, and communication guidelines.
    """
    __tablename__ = "ai_knowledge_base"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(50), index=True)           # example_nudge, product_info, terminology, guideline
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)                              # The actual knowledge/example
    language: Mapped[str] = mapped_column(String(30), default="all")        # all, hinglish_80, english_only, etc.
    priority: Mapped[int] = mapped_column(Integer, default=5)               # 1-10, higher = more important
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─────────────────────────────────────────────────────────
#  CHECK-IN / CHECK-OUT  (sales rep visit tracking)
# ─────────────────────────────────────────────────────────
class CheckIn(Base):
    """
    Check-in/check-out records for sales rep visits to customers.
    Synced from CRM API.
    """
    __tablename__ = "checkins"
    __table_args__ = (
        UniqueConstraint('emp_code', 'comp_code', 'checkin_date', 'checkin_time', name='uix_checkin_unique'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crm_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True, index=True)  # CRM's ID field
    emp_code: Mapped[str] = mapped_column(String(20), index=True)           # Employee code
    emp_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    comp_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    comp_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    checkin_date: Mapped[str] = mapped_column(String(20), index=True)       # DD-MM-YYYY
    checkin_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # HH:MM:SS
    checkout_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latitude: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    longitude: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comment_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("crm_comments.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

