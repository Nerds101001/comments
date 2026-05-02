"""
Adaptive writing style learner.

Every real Mukul message, approved AI message, or Gmail-sourced message
is stored as a StyleSample. When enough samples accumulate, we call Claude
to distil a StyleProfile — a compact summary of Mukul's writing patterns
for each language key. This profile is then injected into every generation
prompt so the AI progressively improves at mimicking Mukul's voice.
"""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import StyleSample, StyleProfile
from app.config import settings

logger = logging.getLogger(__name__)

REFRESH_EVERY_N_SAMPLES = 10   # Regenerate style summary after this many new samples


LANGUAGE_LABELS = {
    "hinglish_80":         "80% English / 20% Hindi",
    "hinglish_60":         "60% English / 40% Hindi",
    "english_light_hindi": "mostly English with light Hindi accents",
    "english_only":        "pure professional English",
}


async def add_sample(
    db: AsyncSession,
    *,
    text: str,
    source: str,             # real_message | edited_ai | approved_ai | gmail
    rep_language: str = "hinglish_80",
    context_type: Optional[str] = None,   # nudge | followup | escalation | senior_briefing
) -> None:
    """Store a sample and trigger a style-profile refresh if warranted."""
    if not text or len(text.strip()) < 10:
        return

    sample = StyleSample(
        source=source,
        text=text.strip(),
        rep_language=rep_language,
        context_type=context_type,
        approved=True,
        created_at=datetime.utcnow(),
    )
    db.add(sample)
    await db.commit()

    # Check if we should refresh the profile for this language
    count_result = await db.execute(
        select(func.count()).where(StyleSample.rep_language == rep_language)
    )
    total = count_result.scalar_one()

    profile_result = await db.execute(
        select(StyleProfile).where(StyleProfile.language_key == rep_language)
    )
    profile = profile_result.scalar_one_or_none()

    if profile is None or (total - profile.sample_count) >= REFRESH_EVERY_N_SAMPLES:
        await _refresh_profile(db, rep_language)


async def _refresh_profile(db: AsyncSession, language_key: str) -> None:
    """Ask Claude to distil the latest samples into a writing-style summary."""
    if not settings.CLAUDE_API_KEY:
        return

    result = await db.execute(
        select(StyleSample)
        .where(StyleSample.rep_language == language_key, StyleSample.approved == True)
        .order_by(StyleSample.created_at.desc())
        .limit(60)
    )
    samples = result.scalars().all()
    if not samples:
        return

    lang_label = LANGUAGE_LABELS.get(language_key, language_key)
    examples = "\n\n".join(f"[{i+1}] {s.text}" for i, s in enumerate(samples))

    prompt = f"""You are analysing WhatsApp messages written by Mukul Sareen, founder/CEO of Hi-Tech International Group.
Language register for these messages: {lang_label}.

Here are {len(samples)} real messages Mukul has written to his sales reps:

{examples}

Analyse these messages and write a STYLE GUIDE (max 300 words) that captures:
1. Sentence structure patterns (short/long, imperative, conditional)
2. Characteristic words/phrases Mukul uses
3. Tone (direct, friendly, firm, urgent vs gentle)
4. How he opens messages (first-name, no greeting, etc.)
5. How he closes (Revert / Update me / Confirm EOD / etc.)
6. How he handles Hindi/English mix (for this language register)
7. What he NEVER does (avoid these patterns)

This style guide will be injected into every future message generation so the AI writes exactly like Mukul.
Output ONLY the style guide, no preamble."""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                settings.CLAUDE_API_URL,
                headers={
                    "x-api-key": settings.CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.CLAUDE_MODEL,
                    "max_tokens": 600,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            summary = "".join(
                b["text"] for b in data.get("content", []) if b.get("type") == "text"
            ).strip()
    except Exception as exc:
        logger.warning("Style profile refresh failed for %s: %s", language_key, exc)
        return

    # Count total samples
    count_result = await db.execute(
        select(func.count()).where(StyleSample.rep_language == language_key)
    )
    total = count_result.scalar_one()

    # Upsert profile
    profile_result = await db.execute(
        select(StyleProfile).where(StyleProfile.language_key == language_key)
    )
    profile = profile_result.scalar_one_or_none()

    if profile:
        profile.summary = summary
        profile.sample_count = total
        profile.generated_at = datetime.utcnow()
    else:
        db.add(StyleProfile(
            language_key=language_key,
            summary=summary,
            sample_count=total,
            generated_at=datetime.utcnow(),
        ))

    await db.commit()
    logger.info("Style profile refreshed for language=%s (%d samples)", language_key, total)


async def get_style_context(db: AsyncSession, language_key: str) -> str:
    """
    Return a block of text to inject into generation prompts.
    Includes the cached style-profile summary + a few recent examples.
    """
    profile_result = await db.execute(
        select(StyleProfile).where(StyleProfile.language_key == language_key)
    )
    profile = profile_result.scalar_one_or_none()

    recent_result = await db.execute(
        select(StyleSample)
        .where(StyleSample.rep_language == language_key, StyleSample.approved == True)
        .order_by(StyleSample.created_at.desc())
        .limit(5)
    )
    recents = recent_result.scalars().all()

    parts: list[str] = []

    if profile:
        parts.append(f"MUKUL'S STYLE PROFILE (learned from {profile.sample_count} real messages):\n{profile.summary}")

    if recents:
        examples = "\n".join(f"  • {s.text[:150]}" for s in recents)
        parts.append(f"RECENT REAL MESSAGES (for tone reference):\n{examples}")

    return "\n\n".join(parts) if parts else ""
