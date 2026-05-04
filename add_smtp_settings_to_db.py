"""
Migration: Add SMTP settings to app_settings table.
This allows SMTP configuration to be saved and updated via the UI.
"""
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.models import AppSetting


async def add_smtp_settings():
    """Add SMTP settings to app_settings if they don't exist."""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # SMTP settings to add
        smtp_settings = [
            ("smtp_host", ""),
            ("smtp_port", "587"),
            ("smtp_user", ""),
            ("smtp_password", ""),
            ("smtp_from_name", "Hi-Tech AI Sales"),
            ("smtp_from_address", ""),
        ]
        
        added_count = 0
        for key, default_value in smtp_settings:
            result = await db.execute(
                select(AppSetting).where(AppSetting.key == key)
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                setting = AppSetting(
                    key=key,
                    value=default_value,
                    updated_at=datetime.utcnow()
                )
                db.add(setting)
                added_count += 1
                print(f"✅ Added {key} setting")
            else:
                print(f"ℹ️  {key} setting already exists")
        
        await db.commit()
        
        if added_count > 0:
            print(f"\n✅ Added {added_count} SMTP settings to database")
        else:
            print("\nℹ️  All SMTP settings already exist")
        
        print("\n📊 Current SMTP settings:")
        result = await db.execute(
            select(AppSetting).where(
                AppSetting.key.in_([s[0] for s in smtp_settings])
            )
        )
        settings = result.scalars().all()
        for s in settings:
            value_display = s.value if s.key != "smtp_password" else ("***" if s.value else "")
            print(f"   {s.key}: {value_display}")


if __name__ == "__main__":
    asyncio.run(add_smtp_settings())
