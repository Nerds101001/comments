"""
Timezone utilities for Indian Standard Time (IST).
All times in the application should be displayed in IST.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

# IST is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))


def utc_to_ist(dt: datetime) -> datetime:
    """Convert UTC datetime to IST."""
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)


def ist_to_utc(dt: datetime) -> datetime:
    """Convert IST datetime to UTC."""
    if dt.tzinfo is None:
        # Assume IST if no timezone info
        dt = dt.replace(tzinfo=IST)
    return dt.astimezone(timezone.utc)


def now_ist() -> datetime:
    """Get current time in IST."""
    return datetime.now(IST)


def now_utc() -> datetime:
    """Get current time in UTC (for database storage)."""
    return datetime.now(timezone.utc)


def format_ist(dt: datetime, format_str: str = "%d-%m-%Y %H:%M:%S IST") -> str:
    """Format datetime in IST with custom format."""
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime(format_str)


def format_ist_time(dt: datetime) -> str:
    """Format time only in IST (HH:MM format)."""
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime("%H:%M")


def format_ist_date(dt: datetime) -> str:
    """Format date only in IST (DD-MM-YYYY format)."""
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime("%d-%m-%Y")


def format_ist_datetime(dt: datetime) -> str:
    """Format full datetime in IST (DD-MM-YYYY HH:MM format)."""
    ist_dt = utc_to_ist(dt)
    return ist_dt.strftime("%d-%m-%Y %H:%M")


def parse_ist_date(date_str: str, format_str: str = "%d-%m-%Y") -> datetime:
    """Parse IST date string to UTC datetime for database storage."""
    ist_dt = datetime.strptime(date_str, format_str)
    ist_dt = ist_dt.replace(tzinfo=IST)
    return ist_to_utc(ist_dt)
