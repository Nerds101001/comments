"""
AI Brain — the core intelligence layer.

Responsibilities:
  1. generate_nudge()           — craft next WhatsApp message to a rep in Mukul's voice
  2. generate_senior_briefing() — write the Mukul → Senior escalation message
  3. generate_senior_reply()    — Mukul's follow-up in the Senior thread
  4. evaluate_confidence()      — score how well a rep reply addressed a follow-up question (0-100)
  5. process_crm_comment()      — extract insight from a CRM comment + produce a follow-up question
  6. generate_followup_question()— standalone follow-up question generator

All Claude calls go through the backend (no browser-side API keys).
The style_learner module is called after every real message so the AI learns.
"""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Conversation, Message, SeniorMessage, Rep, Senior, Customer
from app.services import style_learner

logger = logging.getLogger(__name__)

# ── Language instruction blocks ────────────────────────────────────────────────
LANGUAGE_INSTRUCTIONS = {
    "hinglish_80": """\
LANGUAGE BLEND — 80% English / 20% Hindi:
Sentences are English-LED with Hindi sprinkled naturally. Hindi as connectives
(toh, abhi, kal, achha, theek hai, lekin, na, ki, ka, ko), light filler (yaar, ji),
occasional emphasis (PAKKA, sirf). English carries action items, business terms,
products, deadlines.
✓ "Ravi, this 8-minute visit toh basically drive-by hai. What was the real situation?"
✗ "Ravi ji, sirf 8 minute? Comment mein likha hai but 8 min mein meeting nahi hoti.\"""",

    "hinglish_60": """\
LANGUAGE BLEND — 60% English / 40% Hindi:
Hindi is more present — full Hindi clauses are fine, but business terms/products/
deadlines stay English. Use "toh dekho", "matlab", "lekin", "kya kar rahe ho", "abhi tak".
✓ "Vishal, dekho — Patil Engg ke saath relationship 3 saal ka hai. Cross-sell easy hoga,
but proposal aaj jaana chahiye, kal nahi.\"""",

    "english_light_hindi": """\
LANGUAGE — Mostly English (~95%) with very light Hindi accents:
Full English sentences. Occasional "ji", "achha", "thoda" only when warmth is needed.
No Hindi connectives, no Hindi clauses. Professional Indian English.
✓ "Vikas, this customer hasn't ordered in 92 days — that's a 3x deviation from their pattern.\"""",

    "english_only": """\
LANGUAGE — Pure English, no Hindi at all:
Professional, direct, business English. No Hindi words including "ji", "achha", "toh".
✓ "Daniel, the Coimbatore Footwear samples — has dispatch been raised?\"""",
}

INTENSITY_INSTRUCTIONS = {
    "high":     "INTENSITY — HIGH: Rep responds to proactive nudges. Be direct, push hard, ask follow-ups.",
    "standard": "INTENSITY — STANDARD: Nudge on important moments, not every signal.",
    "light":    "INTENSITY — LIGHT: Be concise, only message on critical events or rep replies.",
    "minimal":  "INTENSITY — MINIMAL: Only if absolutely necessary. Very short, critical issues only.",
}


# ─────────────────────────────────────────────────────────────────────────────
#  INTERNAL AI HELPER (NVIDIA OpenAI-compatible API)
# ─────────────────────────────────────────────────────────────────────────────
async def _call_ai(prompt: str, max_tokens: int = 600) -> str:
    """Send a single-turn prompt to NVIDIA AI and return the text response."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.AI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.AI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1,
                "top_p": 1,
                "max_tokens": max_tokens,
                "stream": False,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        
        # Extract response from NVIDIA API
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        # NVIDIA reasoning models return content in "reasoning" or "reasoning_content"
        # Regular models return in "content"
        content = message.get("content")
        reasoning = message.get("reasoning") or message.get("reasoning_content")
        
        # Use reasoning if content is null (reasoning model)
        # Otherwise use content (regular model)
        response_text = content if content else reasoning
        
        if reasoning and content:
            # Both present - log reasoning for debugging
            logger.debug(f"AI Reasoning: {reasoning}")
        
        return (response_text or "").strip()


# ─────────────────────────────────────────────────────────────────────────────
#  1. GENERATE NUDGE  (Mukul → Rep)
# ─────────────────────────────────────────────────────────────────────────────
async def generate_nudge(
    db: AsyncSession,
    conv: Conversation,
    rep: Rep,
    customer: Optional[Customer] = None,
    advisory_only: bool = False,
) -> str:
    lang = rep.language or "hinglish_80"
    intensity = rep.intensity or "standard"

    lang_block = LANGUAGE_INSTRUCTIONS.get(lang, LANGUAGE_INSTRUCTIONS["hinglish_80"])
    intensity_block = INTENSITY_INSTRUCTIONS.get(intensity, INTENSITY_INSTRUCTIONS["standard"])
    style_block = await style_learner.get_style_context(db, lang)
    
    # Get knowledge base context
    knowledge_block = await _get_knowledge_context(db, lang)

    if customer:
        cust_block = (
            f"CUSTOMER:\n"
            f"- {customer.name} ({customer.comp_code}) · {customer.city}, {customer.state}\n"
            f"- Type: {customer.cust_type.upper()}\n"
            f"- Last order: {customer.last_order_days} days ago"
            if customer.last_order_days is not None else "- Last order: never"
        )
        cust_block += (
            f"\n- LTV: {customer.ltv}"
            f"\n- Products bought: {', '.join(customer.products_bought) or 'none yet'}"
            f"\n- Cross-sell opportunities: {', '.join(customer.cross_sell) or 'none flagged'}"
        )
    else:
        cust_block = "CUSTOMER: cluster/multiple leads (see thread intel)"

    thread = "\n\n".join(
        f"[{m.ts}] {'MUKUL (you)' if m.from_who == 'mukul' else rep.name.split()[0].upper() + ' (rep)'}: {m.text}"
        for m in conv.messages
    )

    advisory_note = (
        "\nNOTE: Mukul has personally taken over this thread. "
        "Generate ADVISORY suggestion only — he will review/edit before sending."
        if advisory_only else ""
    )

    prompt = f"""You are Mukul Sareen, founder/CEO of Hi-Tech International Group
(brands: Rust-X, Dr. Bio, Tuffpaulin, KIF, EVA, Fillezy, biopolymer resins).
You are messaging your sales rep on WhatsApp directly.

{lang_block}

{intensity_block}

VOICE: Direct, fast. WhatsApp-style 1-4 lines. Address rep by first name. ONE clear
next action. End with Revert/Update me/Confirm by EOD. Never lecture, never thank
profusely, no placeholders.

{style_block}

{knowledge_block}

REP: {rep.name} (EMP {rep.emp_code}, {rep.region}, role: {rep.role})
{cust_block}

THREAD: {conv.topic}
Stage: {conv.pipeline_stage}
Objective: {conv.objective}
Tactic: {conv.tactic}
Intel: {conv.intel or 'See thread for context'}

CONVERSATION:
{thread}
{advisory_note}

Generate next WhatsApp message to {rep.name.split()[0]}. Output JUST the text."""

    return await _call_ai(prompt, max_tokens=600)


# ─────────────────────────────────────────────────────────────────────────────
#  2. GENERATE SENIOR BRIEFING  (Mukul → Senior)
# ─────────────────────────────────────────────────────────────────────────────
async def generate_senior_briefing(
    db: AsyncSession,
    conv: Conversation,
    senior: Senior,
    rep: Rep,
    customer: Optional[Customer],
) -> str:
    lang = senior.language or "hinglish_80"
    lang_inst = {
        "hinglish_80":         "Write in 80% English with light Hindi connectives (toh, achha, kal, lekin).",
        "hinglish_60":         "Write in 60% English with more natural Hindi flow.",
        "english_light_hindi": "Write in mostly English (95%), occasional ji/achha only.",
        "english_only":        "Write in pure professional English. NO Hindi words.",
    }.get(lang, "Write in 80/20 Hinglish.")

    cust_block = (
        f"Customer: {customer.name} ({customer.comp_code}), {customer.city}, {customer.state}. "
        f"Type: {customer.cust_type}, last order: {customer.last_order_days} days ago, LTV: {customer.ltv}."
        if customer
        else f"Lead/cluster: {conv.topic}"
    )

    transcript = "\n".join(
        f"[{m.ts}] {'Mukul' if m.from_who == 'mukul' else rep.name.split()[0]}: {m.text}"
        for m in conv.messages
    )

    prompt = f"""You are Mukul Sareen, founder/CEO of Hi-Tech International Group.
You are forwarding a problematic sales situation to your senior manager
{senior.name} ({senior.role}) for them to handle.

LANGUAGE FOR SENIOR: {lang_inst}

CONTEXT:
- Sales rep: {rep.name} (EMP {rep.emp_code}, {rep.region})
- {cust_block}
- Topic: {conv.topic}
- Why forwarding: {conv.handler_reason}

FULL CONVERSATION HISTORY between me and {rep.name.split()[0]}:
{transcript}

Write ONE WhatsApp message FROM YOU (Mukul) TO {senior.name.split()[0]} that:
1. Briefly explains the situation in 1-2 lines
2. Pastes the FULL conversation transcript verbatim
3. States exactly what you need {senior.name.split()[0]} to do — be specific
4. Sets a deadline (within {settings.SENIOR_ESCALATION_WINDOW_HOURS}h)
5. Asks them to revert with their decision

Output JUST the message text."""

    return await _call_ai(prompt, max_tokens=1500)


# ─────────────────────────────────────────────────────────────────────────────
#  3. GENERATE SENIOR REPLY  (Mukul's response in Senior thread)
# ─────────────────────────────────────────────────────────────────────────────
async def generate_senior_reply(
    db: AsyncSession,
    conv: Conversation,
    senior: Senior,
    rep: Rep,
) -> str:
    lang = senior.language or "hinglish_80"
    lang_inst = {
        "hinglish_80":         "Write in 80% English with light Hindi connectives.",
        "hinglish_60":         "Write in 60% English with more Hindi flow.",
        "english_light_hindi": "Write in mostly English (95%).",
        "english_only":        "Write in pure professional English. NO Hindi.",
    }.get(lang, "Write in 80/20 Hinglish.")

    senior_thread = "\n\n".join(
        f"[{m.ts}] {'Mukul (you)' if m.from_who == 'ai_to_senior' else senior.name.split()[0]}: {m.text}"
        for m in conv.senior_messages
    )
    rep_transcript = "\n".join(
        f"[{m.ts}] {'Mukul' if m.from_who == 'mukul' else rep.name.split()[0]}: {m.text}"
        for m in conv.messages
    )

    prompt = f"""You are Mukul Sareen, CEO of Hi-Tech International Group.
You are replying to your senior manager {senior.name} about a sales escalation.

LANGUAGE: {lang_inst}
VOICE: Direct, 1-3 lines. Decisive. If they need permission — decide quickly.

BACKGROUND (rep-Mukul conversation):
{rep_transcript}

YOUR CONVERSATION WITH {senior.name.split()[0].upper()} SO FAR:
{senior_thread}

Write your NEXT WhatsApp reply to {senior.name.split()[0]}. Output JUST the text."""

    return await _call_ai(prompt, max_tokens=500)


# ─────────────────────────────────────────────────────────────────────────────
#  4. EVALUATE CONFIDENCE  (how well did the rep reply answer the question?)
# ─────────────────────────────────────────────────────────────────────────────
async def evaluate_confidence(
    question: str,
    rep_reply: str,
    context: str = "",
) -> int:
    """
    Returns 0-100 integer confidence score.
    88+ = resolved, <88 = escalate.
    """
    prompt = f"""You are evaluating whether a sales rep's reply adequately addressed a follow-up question.

FOLLOW-UP QUESTION ASKED:
{question}

REP'S REPLY:
{rep_reply}

CONTEXT:
{context or 'N/A'}

Score the reply on a scale of 0-100:
- 90-100: Complete, specific, actionable answer. No ambiguity. Deal status/next step crystal clear.
- 75-89: Mostly answered. Some detail missing but situation understood.
- 50-74: Partial answer. Key info still unclear.
- 0-49: Vague, deflecting, or didn't address the question.

Reply with ONLY a number (0-100). No explanation."""

    try:
        raw = await _call_ai(prompt, max_tokens=10)
        score = int("".join(c for c in raw if c.isdigit())[:3])
        return min(100, max(0, score))
    except Exception:
        return 50  # default to mid-confidence if scoring fails


# ─────────────────────────────────────────────────────────────────────────────
#  5. PROCESS CRM COMMENT
# ─────────────────────────────────────────────────────────────────────────────
async def process_crm_comment(
    raw_comment: str,
    rep: Rep,
    customer: Optional[Customer] = None,
) -> dict:
    """
    Process a CRM visit comment/note.
    Returns:
      {
        "summary": str,           — concise summary of what happened
        "followup_question": str, — WhatsApp question to ask the rep
        "needs_followup": bool,   — False if comment is already complete
        "urgency": str,           — high/medium/low
      }
    """
    cust_ctx = (
        f"Customer: {customer.name} ({customer.comp_code}), {customer.city}, "
        f"Type: {customer.cust_type}, LTV: {customer.ltv}"
        if customer else "Customer: unknown"
    )

    lang = rep.language or "hinglish_80"
    lang_inst = LANGUAGE_INSTRUCTIONS.get(lang, LANGUAGE_INSTRUCTIONS["hinglish_80"])

    prompt = f"""You are Mukul Sareen's AI assistant processing a CRM visit comment.

REP: {rep.name} (EMP {rep.emp_code}, {rep.region})
{cust_ctx}

CRM COMMENT/VISIT NOTE:
{raw_comment}

Analyse this comment and respond in JSON:
{{
  "summary": "<1-2 sentence summary of what happened in the visit/interaction>",
  "needs_followup": <true if rep's comment leaves important things unclear, false if complete>,
  "urgency": "<high|medium|low based on deal stage and customer risk>",
  "followup_question": "<WhatsApp message to send to rep if needs_followup=true, else null>",
  "key_issues": ["<list of up to 3 key issues or open items>"]
}}

If needs_followup=true, the followup_question should be:
{lang_inst}
- Direct, 1-3 lines in Mukul's voice
- Ask ONE specific thing that's unclear or needs action
- Include deadline (reply by EOD, update by tomorrow, etc.)

Output ONLY valid JSON."""

    try:
        raw = await _call_ai(prompt, max_tokens=600)
        import json
        # Strip markdown code fences if present
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)
    except Exception as exc:
        logger.warning("CRM comment processing failed: %s", exc)
        return {
            "summary": raw_comment[:200],
            "needs_followup": True,
            "urgency": "medium",
            "followup_question": f"{rep.name.split()[0]}, quick update on yesterday's visit?",
            "key_issues": [],
        }


# ─────────────────────────────────────────────────────────────────────────────
#  6. GENERATE FOLLOWUP QUESTION  (standalone)
# ─────────────────────────────────────────────────────────────────────────────
async def generate_followup_question(
    db: AsyncSession,
    context: str,
    rep: Rep,
    customer: Optional[Customer] = None,
) -> str:
    """Generate a single follow-up question from arbitrary context."""
    lang = rep.language or "hinglish_80"
    lang_block = LANGUAGE_INSTRUCTIONS.get(lang, LANGUAGE_INSTRUCTIONS["hinglish_80"])
    style_block = await style_learner.get_style_context(db, lang)

    cust_block = (
        f"Customer: {customer.name} ({customer.cust_type}, {customer.city})"
        if customer else ""
    )

    prompt = f"""You are Mukul Sareen, CEO of Hi-Tech International Group.
{lang_block}
{style_block}

REP: {rep.name} (EMP {rep.emp_code}, {rep.region})
{cust_block}

SITUATION:
{context}

Write ONE sharp follow-up question for the rep. WhatsApp-style, 1-2 lines.
Output JUST the question text."""

    return await _call_ai(prompt, max_tokens=200)



async def _get_knowledge_context(db: AsyncSession, language: str) -> str:
    """Get relevant knowledge base entries for AI context."""
    from sqlalchemy import select
    from app.models import AIKnowledgeBase
    
    # Get active knowledge entries for this language (or "all")
    result = await db.execute(
        select(AIKnowledgeBase)
        .where(AIKnowledgeBase.is_active == True)
        .where(
            (AIKnowledgeBase.language == language) | (AIKnowledgeBase.language == "all")
        )
        .order_by(AIKnowledgeBase.priority.desc())
        .limit(10)  # Top 10 most important entries
    )
    entries = result.scalars().all()
    
    if not entries:
        return ""
    
    # Format knowledge entries by category
    knowledge_sections = {
        "example_nudge": [],
        "product_info": [],
        "terminology": [],
        "guideline": [],
    }
    
    for entry in entries:
        if entry.category in knowledge_sections:
            knowledge_sections[entry.category].append(f"• {entry.title}: {entry.content}")
    
    # Build knowledge block
    blocks = []
    
    if knowledge_sections["example_nudge"]:
        blocks.append("EXAMPLE NUDGES (learn from these):\n" + "\n".join(knowledge_sections["example_nudge"]))
    
    if knowledge_sections["product_info"]:
        blocks.append("PRODUCT KNOWLEDGE:\n" + "\n".join(knowledge_sections["product_info"]))
    
    if knowledge_sections["terminology"]:
        blocks.append("COMPANY TERMINOLOGY:\n" + "\n".join(knowledge_sections["terminology"]))
    
    if knowledge_sections["guideline"]:
        blocks.append("COMMUNICATION GUIDELINES:\n" + "\n".join(knowledge_sections["guideline"]))
    
    if blocks:
        return "\n\n".join(blocks)
    
    return ""
