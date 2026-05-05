"""
Email service for sending emails via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
from typing import Optional, List
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


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
    Send an email via SMTP using settings from database.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Plain text body
        html: HTML body (optional)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        attachments: List of file paths to attach (optional)
    
    Returns:
        True if sent successfully, False otherwise
    """
    # Get SMTP settings from database
    from app.database import AsyncSessionLocal
    from app.models import AppSetting
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        smtp_settings_result = await db.execute(
            select(AppSetting).where(
                AppSetting.key.in_(["smtp_host", "smtp_port", "smtp_user", "smtp_password", "smtp_from_name", "smtp_from_address"])
            )
        )
        smtp_settings_db = {s.key: s.value for s in smtp_settings_result.scalars().all()}
    
    smtp_host = smtp_settings_db.get("smtp_host", settings.EMAIL_SMTP_HOST)
    smtp_port = int(smtp_settings_db.get("smtp_port", str(settings.EMAIL_SMTP_PORT)))
    smtp_user = smtp_settings_db.get("smtp_user", settings.EMAIL_SMTP_USER)
    smtp_password = smtp_settings_db.get("smtp_password", settings.EMAIL_SMTP_PASSWORD)
    from_name = smtp_settings_db.get("smtp_from_name", settings.EMAIL_FROM_NAME)
    from_address = smtp_settings_db.get("smtp_from_address", settings.EMAIL_FROM_ADDRESS or smtp_user)
    
    if not smtp_host or not smtp_user:
        logger.warning("Email not configured. Skipping send.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{from_address}>"
        msg['To'] = to
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = ', '.join(cc)
        if bcc:
            msg['Bcc'] = ', '.join(bcc)
        
        # Attach plain text
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach HTML if provided
        if html:
            msg.attach(MIMEText(html, 'html'))
        
        # Attach files if provided
        if attachments:
            for file_path in attachments:
                if not file_path.exists():
                    logger.warning(f"Attachment not found: {file_path}")
                    continue
                
                with open(file_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {file_path.name}'
                    )
                    msg.attach(part)
        
        import ssl
        context = ssl.create_default_context()

        recipients = [to]
        if cc:
            recipients.extend(cc)
        if bcc:
            recipients.extend(bcc)

        # Try ports in order: 465 (SSL) → 587 (STARTTLS) → 2525 (STARTTLS)
        # Railway blocks 587 outbound, so 465 is tried first.
        ports_to_try = []
        if smtp_port == 465:
            ports_to_try = [(465, "ssl"), (587, "starttls"), (2525, "starttls")]
        elif smtp_port == 587:
            ports_to_try = [(465, "ssl"), (587, "starttls"), (2525, "starttls")]
        else:
            ports_to_try = [(smtp_port, "starttls"), (465, "ssl"), (587, "starttls"), (2525, "starttls")]

        last_error = None
        for port, mode in ports_to_try:
            try:
                if mode == "ssl":
                    with smtplib.SMTP_SSL(smtp_host, port, context=context, timeout=15) as server:
                        server.login(smtp_user, smtp_password)
                        server.send_message(msg, to_addrs=recipients)
                else:
                    with smtplib.SMTP(smtp_host, port, timeout=15) as server:
                        server.ehlo()
                        server.starttls(context=context)
                        server.ehlo()
                        server.login(smtp_user, smtp_password)
                        server.send_message(msg, to_addrs=recipients)
                logger.info(f"Email sent to {to} via {smtp_host}:{port} ({mode})")
                return True
            except OSError as e:
                # Network unreachable / port blocked — try next port
                last_error = e
                logger.warning(f"Port {port} unreachable: {e}, trying next...")
                continue
            except smtplib.SMTPException as e:
                # Auth/protocol error — no point trying other ports with same creds
                last_error = e
                logger.error(f"SMTP error on {port}: {e}")
                break

        logger.error(f"All SMTP ports failed for {to}. Last error: {last_error}")
        return False
        
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


async def send_customer_email(
    customer_email: str,
    customer_name: str,
    subject: str,
    message: str,
    rep_name: str = "Sales Team",
) -> bool:
    """
    Send a professional email to a customer.
    
    Args:
        customer_email: Customer's email address
        customer_name: Customer's name
        subject: Email subject
        message: Email message body
        rep_name: Name of the sales rep
    
    Returns:
        True if sent successfully
    """
    # Create HTML email
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #007AFF; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px 20px; background: #f9f9f9; }}
            .message {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Hi-Tech International Group</h1>
            </div>
            <div class="content">
                <p>Dear {customer_name},</p>
                <div class="message">
                    {message.replace(chr(10), '<br>')}
                </div>
                <div class="signature">
                    <p><strong>{rep_name}</strong><br>
                    Hi-Tech International Group<br>
                    Brands: Rust-X, Dr. Bio, Tuffpaulin, KIF, EVA, Fillezy</p>
                </div>
            </div>
            <div class="footer">
                <p>This email was sent by Hi-Tech AI Sales System</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    plain_text = f"""
Dear {customer_name},

{message}

Best regards,
{rep_name}
Hi-Tech International Group
Brands: Rust-X, Dr. Bio, Tuffpaulin, KIF, EVA, Fillezy

---
This email was sent by Hi-Tech AI Sales System
    """
    
    return await send_email(
        to=customer_email,
        subject=subject,
        body=plain_text.strip(),
        html=html,
    )


async def send_nudge_email(
    rep_email: str,
    rep_name: str,
    customer_name: str,
    crm_comment: str,
    comment_date: str,
    nudge_text: str,
    mukul_name: str = "Mukul Sareen",
) -> bool:
    """
    Send a nudge email to a sales rep.
    Shows their original CRM field comment + Mukul's follow-up message.
    No AI mentions — reads as a direct message from Mukul.
    """
    first_name = rep_name.split()[0]

    plain = f"""Hi {first_name},

Here is a follow-up regarding your recent visit to {customer_name}.

Your field note ({comment_date}):
"{crm_comment}"

Message from {mukul_name}:

{nudge_text}

---
{mukul_name}
Hi-Tech International Group
Brands: Rust-X · Dr. Bio · Tuffpaulin · KIF · EVA · Fillezy
"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin:0; padding:0; background:#f4f4f4; font-family: Arial, sans-serif; color:#222; }}
  .wrap {{ max-width:620px; margin:32px auto; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,.08); }}
  .header {{ background:#1a1a2e; padding:24px 32px; }}
  .header-title {{ color:#fff; font-size:18px; font-weight:700; margin:0; }}
  .header-sub {{ color:#aaa; font-size:12px; margin:4px 0 0; }}
  .body {{ padding:32px; }}
  .greeting {{ font-size:15px; margin-bottom:24px; }}
  .section-label {{ font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:#888; margin-bottom:8px; }}
  .comment-box {{ background:#f8f8f8; border-left:3px solid #ccc; border-radius:4px; padding:14px 18px; margin-bottom:24px; font-size:14px; color:#444; line-height:1.6; }}
  .comment-meta {{ font-size:11px; color:#999; margin-bottom:8px; }}
  .nudge-box {{ background:#fff8e1; border-left:3px solid #f5a623; border-radius:4px; padding:16px 20px; font-size:15px; line-height:1.7; color:#222; }}
  .footer {{ background:#f4f4f4; padding:20px 32px; border-top:1px solid #e8e8e8; }}
  .footer-name {{ font-weight:700; font-size:13px; color:#333; }}
  .footer-company {{ font-size:12px; color:#666; margin-top:2px; }}
  .footer-brands {{ font-size:11px; color:#999; margin-top:4px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <p class="header-title">Hi-Tech International Group</p>
    <p class="header-sub">Sales Follow-up</p>
  </div>
  <div class="body">
    <p class="greeting">Hi {first_name},</p>
    <p style="font-size:14px;color:#555;margin-bottom:20px;">
      Here is a follow-up regarding your recent visit to <strong>{customer_name}</strong>.
    </p>

    <div class="section-label">Your field note &nbsp;·&nbsp; {comment_date}</div>
    <div class="comment-box">
      &ldquo;{crm_comment}&rdquo;
    </div>

    <div class="section-label">Message from {mukul_name}</div>
    <div class="nudge-box">
      {nudge_text.replace(chr(10), '<br>')}
    </div>
  </div>
  <div class="footer">
    <div class="footer-name">{mukul_name}</div>
    <div class="footer-company">Hi-Tech International Group</div>
    <div class="footer-brands">Rust-X &nbsp;·&nbsp; Dr. Bio &nbsp;·&nbsp; Tuffpaulin &nbsp;·&nbsp; KIF &nbsp;·&nbsp; EVA &nbsp;·&nbsp; Fillezy</div>
  </div>
</div>
</body>
</html>"""

    subject = f"Follow-up: {customer_name} — Action Required"

    return await send_email(
        to=rep_email,
        subject=subject,
        body=plain,
        html=html,
    )
    """Test email SMTP connection using settings stored in the database."""
    from app.database import AsyncSessionLocal
    from app.models import AppSetting
    from sqlalchemy import select
    import ssl

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(AppSetting).where(
                AppSetting.key.in_(["smtp_host", "smtp_port", "smtp_user", "smtp_password"])
            )
        )
        db_settings = {s.key: s.value for s in result.scalars().all()}

    smtp_host = db_settings.get("smtp_host") or settings.EMAIL_SMTP_HOST
    smtp_port = int(db_settings.get("smtp_port") or settings.EMAIL_SMTP_PORT)
    smtp_user = db_settings.get("smtp_user") or settings.EMAIL_SMTP_USER
    smtp_password = db_settings.get("smtp_password") or settings.EMAIL_SMTP_PASSWORD

    if not smtp_host or not smtp_user or not smtp_password:
        return {
            "success": False,
            "error": "Email not configured. Please set SMTP Host, Username and Password in Settings."
        }

    try:
        ctx = ssl.create_default_context()
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ctx, timeout=15) as server:
                server.login(smtp_user, smtp_password)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=ctx)
                server.ehlo()
                server.login(smtp_user, smtp_password)

        return {
            "success": True,
            "message": f"Connected to {smtp_host}:{smtp_port} as {smtp_user}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
