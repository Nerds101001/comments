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
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            
            recipients = [to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            server.send_message(msg, to_addrs=recipients)
        
        logger.info(f"Email sent successfully to {to}")
        return True
        
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


async def test_email_connection() -> dict:
    """Test email SMTP connection."""
    if not settings.EMAIL_SMTP_HOST or not settings.EMAIL_SMTP_USER:
        return {
            "success": False,
            "error": "Email not configured. Please set EMAIL_SMTP_HOST and EMAIL_SMTP_USER in .env"
        }
    
    try:
        with smtplib.SMTP(settings.EMAIL_SMTP_HOST, settings.EMAIL_SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(settings.EMAIL_SMTP_USER, settings.EMAIL_SMTP_PASSWORD)
        
        return {
            "success": True,
            "message": f"Connected to {settings.EMAIL_SMTP_HOST} as {settings.EMAIL_SMTP_USER}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
