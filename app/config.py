from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # ── App ─────────────────────────────────
    APP_SECRET_KEY: str = "change-me-in-production"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # ── Database ─────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./hitech_sales.db"

    # ── AI API (NVIDIA) ──────────────────────
    AI_API_KEY: str = ""
    AI_MODEL: str = "openai/gpt-oss-120b"
    AI_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    AI_PROVIDER: str = "nvidia"  # nvidia or claude

    # ── WhatsApp Meta Cloud API ──────────────
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "hitech-verify-2026"
    WHATSAPP_API_VERSION: str = "v20.0"
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None
    META_BUSINESS_ID: Optional[str] = None
    META_APP_ID: Optional[str] = None
    META_SYSTEM_USER_ID: Optional[str] = None

    # ── AiSensy WhatsApp API ─────────────────
    AISENSY_API_KEY: str = ""
    AISENSY_USERNAME: str = "Hi Tech Group 8161"

    # ── CRM (rustx.net) ──────────────────────
    CRM_BASE_URL: str = "https://api-crm.rustx.net"
    CRM_TOKEN: str = ""
    CRM_USERNAME: str = ""
    CRM_PASSWORD: str = ""
    CRM_POLL_INTERVAL_MINUTES: int = 10080  # Auto-sync every 7 days (10080 min = 1 week)
    CRM_ADMIN_EMP_CODE: str = "1494"     # Nagender — admin user with full data access

    # ── Gmail (optional) ─────────────────────
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:8002/api/gmail/callback"

    # ── Email SMTP ───────────────────────────
    EMAIL_SMTP_HOST: str = ""
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_USER: str = ""
    EMAIL_SMTP_PASSWORD: str = ""
    EMAIL_FROM_NAME: str = "Hi-Tech AI Sales"
    EMAIL_FROM_ADDRESS: str = ""

    # ── Brevo (HTTP email API — works on Railway, no SMTP ports needed) ──
    BREVO_API_KEY: str = ""  # Free at https://app.brevo.com → SMTP & API → API Keys

    # ── Owner ────────────────────────────────
    MUKUL_PHONE: str = ""
    MUKUL_NAME: str = "Mukul Sareen"

    # ── App Password (login gate) ─────────────────────────────────────────
    APP_PASSWORD: str = "Rustx@3100"

    # ── Escalation ───────────────────────────
    AI_CONFIDENCE_THRESHOLD: int = 88
    SENIOR_ESCALATION_WINDOW_HOURS: int = 24
    PRICING_AUTHORITY_PCT: int = 8
    KEY_ACCOUNT_LTV_THRESHOLD: int = 2_000_000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
