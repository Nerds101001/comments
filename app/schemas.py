"""
Pydantic v2 schemas for request/response validation.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────
#  SENIOR
# ─────────────────────────────────────────────────────────
class SeniorBase(BaseModel):
    name: str
    role: str = "Senior Sales Manager"
    phone: str
    avatar: str
    color: str = "#5856D6"
    region: str = ""
    language: str = "english_only"
    enabled: bool = True

class SeniorCreate(SeniorBase):
    id: str

class SeniorOut(SeniorBase):
    id: str
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────
#  REP
# ─────────────────────────────────────────────────────────
class RepBase(BaseModel):
    name: str
    emp_code: str
    phone: str
    region: str = ""
    avatar: str
    color: str = "#007AFF"
    intensity: str = "standard"
    language: str = "hinglish_80"
    role: str = "Sales Person"
    reports_to_id: Optional[str] = None
    is_active: bool = True
    email: Optional[str] = None

class RepCreate(RepBase):
    id: str

class RepOut(RepBase):
    id: str
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────
#  CUSTOMER
# ─────────────────────────────────────────────────────────
class CustomerBase(BaseModel):
    comp_code: str
    name: str
    city: str = ""
    state: str = ""
    cust_type: str = "new"
    last_order_days: Optional[int] = None
    products_bought: List[str] = []
    ltv: str = "unknown"
    cross_sell: List[str] = []
    phone: Optional[str] = None

class CustomerCreate(CustomerBase):
    id: str

class CustomerOut(CustomerBase):
    id: str
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────
#  MESSAGE
# ─────────────────────────────────────────────────────────
class MessageOut(BaseModel):
    id: int
    from_who: str
    text: str
    ts: str
    date_label: str
    status: str
    is_read: bool
    by_ai: bool
    by_mukul_real: bool
    requires_approval: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class MessageCreate(BaseModel):
    from_who: str
    text: str
    by_mukul_real: bool = False

class SeniorMessageOut(BaseModel):
    id: int
    from_who: str
    text: str
    ts: str
    date_label: str
    status: str
    is_read: bool
    created_at: datetime
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────
#  CONVERSATION
# ─────────────────────────────────────────────────────────
class ConversationOut(BaseModel):
    id: str
    rep_id: str
    customer_id: Optional[str]
    topic: str
    pipeline_stage: str
    objective: str
    tactic: str
    intel: Optional[str]
    urgency: str
    handler: str
    handler_reason: Optional[str]
    senior_assigned_id: Optional[str]
    ai_confidence: int
    is_fresh: bool
    is_resolved: bool
    crm_ref: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut] = []
    senior_messages: List[SeniorMessageOut] = []
    # Nested objects for frontend convenience
    rep: Optional[RepOut] = None
    customer: Optional[CustomerOut] = None
    senior_assigned: Optional[SeniorOut] = None
    model_config = {"from_attributes": True}

class ConversationCreate(BaseModel):
    rep_id: str
    customer_id: Optional[str] = None
    topic: str
    pipeline_stage: str = ""
    objective: str = ""
    tactic: str = ""
    intel: Optional[str] = None
    urgency: str = "medium"
    handler: str = "ai"

class ConversationUpdate(BaseModel):
    topic: Optional[str] = None
    pipeline_stage: Optional[str] = None
    objective: Optional[str] = None
    tactic: Optional[str] = None
    intel: Optional[str] = None
    urgency: Optional[str] = None
    handler: Optional[str] = None
    handler_reason: Optional[str] = None
    senior_assigned_id: Optional[str] = None
    ai_confidence: Optional[int] = None
    is_fresh: Optional[bool] = None
    is_resolved: Optional[bool] = None


# ─────────────────────────────────────────────────────────
#  AI GENERATE
# ─────────────────────────────────────────────────────────
class GenerateNudgeResponse(BaseModel):
    text: str
    advisory: bool = False
    confidence: Optional[int] = None


# ─────────────────────────────────────────────────────────
#  CRM COMMENT
# ─────────────────────────────────────────────────────────
class CRMCommentOut(BaseModel):
    id: int
    crm_comment_id: Optional[str]
    rep_id: Optional[str]
    customer_id: Optional[str]
    crm_emp_code: Optional[str]
    crm_comp_code: Optional[str]
    raw_text: str
    comment_date: Optional[str]
    processed_summary: Optional[str]
    followup_question: Optional[str]
    followup_sent: bool
    rep_reply: Optional[str]
    confidence_score: Optional[int]
    resolution_status: str
    conversation_id: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_conversations: int
    escalated: int
    approval_pending: int
    with_senior: int
    ai_autonomous: int
    mukul_handling: int
    nudges_sent: int
    rep_replies: int
    drafts_pending: int
    crm_comments_pending: int
    crm_comments_resolved_today: int


# ─────────────────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────────────────
class IntegrationStatus(BaseModel):
    connected: bool
    last_check: Optional[str] = None
    error: Optional[str] = None

class SettingsOut(BaseModel):
    team: List[RepOut]
    seniors: List[SeniorOut]
    integrations: dict
    escalation_rules: dict
    senior_layer: dict


# ─────────────────────────────────────────────────────────
#  WHATSAPP
# ─────────────────────────────────────────────────────────
class WhatsAppSendRequest(BaseModel):
    to: str
    text: str
    conversation_id: Optional[str] = None


# ─────────────────────────────────────────────────────────
#  GENERIC
# ─────────────────────────────────────────────────────────
class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Any] = None
