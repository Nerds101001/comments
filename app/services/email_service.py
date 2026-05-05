"""
Email service — sends via Brevo HTTP API (primary) with SMTP fallback.

Railway blocks all outbound SMTP ports (465/587/2525).
Brevo's HTTP API works on any host with no port restrictions.

Setup (one-time, free):
  1. Sign up at https://app.brevo.com  (free — 300 emails/day)
  2. Go to SMTP & API → API Keys → Create a new API key
  3. Add sender domain: hitechgroup.in  (verify via DNS or email)
  4. Add BREVO_API_KEY to Railway env vars
     OR save it via Settings page → Email section → Brevo API Key field
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from pathlib import Path

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────

async def _get_email_cfg() -> dict:
    """Load email settings from DB, falling back to env vars."""
    from app.database import AsyncSessionLocal
    from app.models import AppSetting
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AppSetting).where(
                AppSetting.key.in_([
                    "smtp_host", "smtp_port", "smtp_user", "smtp_password",
                    "smtp_from_name", "smtp_from_address", "brevo_api_key",
                ])
            )
        )
        db_cfg = {s.key: s.value for s in result.scalars().all()}

    return {
        "host":          db_cfg.get("smtp_host",         settings.EMAIL_SMTP_HOST),
        "port":          int(db_cfg.get("smtp_port",     str(settings.EMAIL_SMTP_PORT))),
        "user":          db_cfg.get("smtp_user",         settings.EMAIL_SMTP_USER),
        "password":      db_cfg.get("smtp_password",     settings.EMAIL_SMTP_PASSWORD),
        "from_name":     db_cfg.get("smtp_from_name",    settings.EMAIL_FROM_NAME),
        "from_address":  db_cfg.get("smtp_from_address", settings.EMAIL_FROM_ADDRESS),
        "brevo_api_key": db_cfg.get("brevo_api_key",     getattr(settings, "BREVO_API_KEY", "")),
    }


async def _send_via_brevo(cfg: dict, to: str, subject: str, html: str, plain: str) -> bool:
    """Send via Brevo transactional API — no SMTP ports, works on Railway."""
    api_key = cfg.get("brevo_api_key", "")
    if not api_key:
        return False

    from_addr = cfg["from_address"] or cfg["user"]
    from_name = cfg["from_name"] or "Hi-Tech AI Sales"

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={"api-key": api_key, "Content-Type": "application/json"},
                json={
                    "sender":      {"name": from_name, "email": from_addr},
                    "to":          [{"email": to}],
                    "subject":     subject,
                    "htmlContent": html,
                    "textContent": plain,
                },
            )
        if resp.status_code in (200, 201):
            logger.info(f"Email sent via Brevo to {to}")
            return True
        logger.error(f"Brevo API {resp.status_code}: {resp.text[:200]}")
        return False
    except Exception as e:
        logger.error(f"Brevo send failed: {e}")
        return False


async def _send_via_smtp(cfg: dict, msg, recipients: list) -> bool:
    """Try SMTP with port fallback: 465 SSL → 587 STARTTLS → 2525 STARTTLS."""
    import ssl
    ctx = ssl.create_default_context()
    host, user, password = cfg["host"], cfg["user"], cfg["password"]

    for port, mode in [(465, "ssl"), (587, "starttls"), (2525, "starttls")]:
        try:
            if mode == "ssl":
                with smtplib.SMTP_SSL(host, port, context=ctx, timeout=15) as s:
                    s.login(user, password)
                    s.send_message(msg, to_addrs=recipients)
            else:
                with smtplib.SMTP(host, port, timeout=15) as s:
                    s.ehlo(); s.starttls(context=ctx); s.ehlo()
                    s.login(user, password)
                    s.send_message(msg, to_addrs=recipients)
            logger.info(f"Email sent via SMTP {host}:{port}")
            return True
        except OSError:
            logger.warning(f"SMTP port {port} blocked, trying next...")
            continue
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error on {port}: {e}")
            break

    logger.error("All SMTP ports failed.")
    return False


# ─────────────────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────────────────

async def send_email(
    to: str,
    subject: str,
    body: str,
    html: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[Path]] = None,
) -> bool:
    """
    Send an email. Tries Brevo API first, falls back to SMTP.

    Args:
        to: Recipient email
        subject: Subject line
        body: Plain text body
        html: HTML body (optional)
        cc / bcc: Extra recipients (optional)
        attachments: File paths to attach (optional)
    """
    cfg = await _get_email_cfg()

    if not cfg["user"] and not cfg["brevo_api_key"]:
        logger.warning("Email not configured — skipping send.")
        return False

    plain    = body
    html_out = html or f"<pre>{body}</pre>"

    # ── Brevo first (works on Railway) ────────────────────────────────────
    if cfg.get("brevo_api_key"):
        if await _send_via_brevo(cfg, to, subject, html_out, plain):
            return True
        logger.warning("Brevo failed, trying SMTP fallback...")

    # ── SMTP fallback ─────────────────────────────────────────────────────
    if not cfg["host"] or not cfg["user"] or not cfg["password"]:
        logger.warning("SMTP not configured — cannot fallback.")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"]    = f"{cfg['from_name']} <{cfg['from_address'] or cfg['user']}>"
    msg["To"]      = to
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg.attach(MIMEText(plain,    "plain"))
    msg.attach(MIMEText(html_out, "html"))

    if attachments:
        for fp in attachments:
            if not fp.exists():
                continue
            with open(fp, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={fp.name}")
                msg.attach(part)

    recipients = [to] + (cc or []) + (bcc or [])
    return await _send_via_smtp(cfg, msg, recipients)


async def send_customer_email(
    customer_email: str,
    customer_name: str,
    subject: str,
    message: str,
    rep_name: str = "Sales Team",
) -> bool:
    """Send a professional email to a customer."""
    html = f"""<!DOCTYPE html>
<html><head><style>
  body{{font-family:Arial,sans-serif;line-height:1.6;color:#333}}
  .wrap{{max-width:600px;margin:0 auto;padding:20px}}
  .header{{background:#007AFF;color:#fff;padding:20px;text-align:center}}
  .content{{padding:30px 20px;background:#f9f9f9}}
  .msg{{background:#fff;padding:20px;border-radius:8px;margin:20px 0}}
  .footer{{text-align:center;padding:20px;color:#666;font-size:12px}}
  .sig{{margin-top:30px;padding-top:20px;border-top:1px solid #ddd}}
</style></head><body>
<div class="wrap">
  <div class="header"><h1>Hi-Tech International Group</h1></div>
  <div class="content">
    <p>Dear {customer_name},</p>
    <div class="msg">{message.replace(chr(10), '<br>')}</div>
    <div class="sig">
      <p><strong>{rep_name}</strong><br>
      Hi-Tech International Group<br>
      Brands: Rust-X, Dr. Bio, Tuffpaulin, KIF, EVA, Fillezy</p>
    </div>
  </div>
  <div class="footer"><p>Sent by Hi-Tech AI Sales System</p></div>
</div></body></html>"""

    plain = f"Dear {customer_name},\n\n{message}\n\nBest regards,\n{rep_name}\nHi-Tech International Group"
    return await send_email(to=customer_email, subject=subject, body=plain, html=html)


async def send_nudge_email(
    rep_email: str,
    rep_name: str,
    customer_name: str,
    crm_comment: str,
    comment_date: str,
    nudge_text: str,
    mukul_name: str = "Mukul Sareen",
) -> bool:
    """Send a nudge email to a sales rep (reads as a direct message from Mukul)."""
    first_name = rep_name.split()[0]
    subject    = f"Follow-up: {customer_name} — Action Required"

    plain = (
        f"Hi {first_name},\n\n"
        f"Follow-up on your visit to {customer_name}.\n\n"
        f"Your field note ({comment_date}):\n\"{crm_comment}\"\n\n"
        f"Message from {mukul_name}:\n\n{nudge_text}\n\n"
        f"---\n{mukul_name}\nHi-Tech International Group\n"
        f"Rust-X · Dr. Bio · Tuffpaulin · KIF · EVA · Fillezy"
    )

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  body{{margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;color:#222}}
  .wrap{{max-width:620px;margin:32px auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
  .hdr{{background:#1a1a2e;padding:24px 32px}}
  .hdr h2{{color:#fff;font-size:18px;margin:0}}
  .hdr p{{color:#aaa;font-size:12px;margin:4px 0 0}}
  .body{{padding:32px}}
  .lbl{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#888;margin-bottom:8px}}
  .cbox{{background:#f8f8f8;border-left:3px solid #ccc;border-radius:4px;padding:14px 18px;margin-bottom:24px;font-size:14px;color:#444;line-height:1.6}}
  .nbox{{background:#fff8e1;border-left:3px solid #f5a623;border-radius:4px;padding:16px 20px;font-size:15px;line-height:1.7;color:#222}}
  .ftr{{background:#f4f4f4;padding:20px 32px;border-top:1px solid #e8e8e8}}
  .ftr b{{font-size:13px;color:#333}}
  .ftr p{{font-size:12px;color:#666;margin:2px 0}}
</style></head><body>
<div class="wrap">
  <div class="hdr"><h2>Hi-Tech International Group</h2><p>Sales Follow-up</p></div>
  <div class="body">
    <p>Hi {first_name},</p>
    <p style="font-size:14px;color:#555">Follow-up on your visit to <strong>{customer_name}</strong>.</p>
    <div class="lbl">Your field note · {comment_date}</div>
    <div class="cbox">&ldquo;{crm_comment}&rdquo;</div>
    <div class="lbl">Message from {mukul_name}</div>
    <div class="nbox">{nudge_text.replace(chr(10), '<br>')}</div>
  </div>
  <div class="ftr">
    <b>{mukul_name}</b>
    <p>Hi-Tech International Group</p>
    <p style="color:#999;font-size:11px">Rust-X · Dr. Bio · Tuffpaulin · KIF · EVA · Fillezy</p>
  </div>
</div></body></html>"""

    return await send_email(to=rep_email, subject=subject, body=plain, html=html)
