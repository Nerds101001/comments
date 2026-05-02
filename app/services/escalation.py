"""
Escalation engine.

Decides whether a rep reply warrants escalation, to whom, and why.
Also handles the routing logic (senior layer vs direct to Mukul).
"""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Tuple, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Conversation, Rep, Senior

logger = logging.getLogger(__name__)


async def should_escalate(
    confidence_score: int,
    conv: Conversation,
    rep: Rep,
) -> Tuple[bool, str, str]:
    """
    Returns (should_escalate, escalation_target, reason)
    escalation_target: 'senior' | 'mukul'
    """
    threshold = settings.AI_CONFIDENCE_THRESHOLD  # default 88

    if confidence_score >= threshold:
        return False, "", ""

    # Determine target
    reason_parts = [f"Rep reply confidence {confidence_score}% is below {threshold}% threshold."]

    # Always-Mukul conditions (bypass senior layer)
    if conv.urgency == "high" and not rep.reports_to_id:
        reason_parts.append("High urgency with no senior assigned — direct to Mukul.")
        return True, "mukul", " ".join(reason_parts)

    # Route to senior if rep has a reporting senior
    if rep.reports_to_id:
        reason_parts.append(
            f"Routing to senior manager first ({rep.reports_to_id.title()}). "
            f"They have {settings.SENIOR_ESCALATION_WINDOW_HOURS}h to resolve before bumping to Mukul."
        )
        return True, "senior", " ".join(reason_parts)

    # No senior — straight to Mukul
    reason_parts.append("No senior layer configured — escalating directly to Mukul.")
    return True, "mukul", " ".join(reason_parts)


def should_require_approval(
    message_text: str,
    conv: Conversation,
) -> bool:
    """
    Returns True if a generated message should be held for Mukul's approval
    before being sent — e.g. when it references Mukul's personal commitment.
    """
    trigger_phrases = [
        "personally", "main khud", "i will come", "i'll come",
        "i am coming", "main aaunga", "main handle",
        "exception pricing", "special approval", "i approve",
        "i'll handle", "main personally",
    ]
    lower = message_text.lower()
    return any(p in lower for p in trigger_phrases)


def classify_urgency(
    comment_text: str,
    customer_type: Optional[str] = None,
    last_order_days: Optional[int] = None,
) -> str:
    """
    Simple rule-based urgency classification for CRM comments.
    The AI brain can override this with its own assessment.
    """
    lower = comment_text.lower()

    high_signals = [
        "urgent", "immediately", "switching", "competitor",
        "lost", "cancel", "no order", "final decision",
        "15%", "last chance", "walking away",
    ]
    low_signals = [
        "follow up next month", "will call later",
        "no update", "same as before",
    ]

    if any(s in lower for s in high_signals):
        return "high"
    if customer_type in ("dormant", "at_risk"):
        return "high"
    if last_order_days and last_order_days > 60:
        return "high"
    if any(s in lower for s in low_signals):
        return "low"
    return "medium"
