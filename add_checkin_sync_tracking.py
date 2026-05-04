"""
Add check-in sync tracking to app_settings table.
This allows tracking when check-ins were last synced separately from comments.
"""
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.models import AppSetting


async def add_checkin_sync_tracking():
    """Add last_checkin_sync setting if it doesn't exist."""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # Check if last_checkin_sync exists
        result = await db.execute(
            select(AppSetting).where(AppSetting.key == "last_checkin_sync")
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            # Add the setting
            setting = AppSetting(
                key="last_checkin_sync",
                value=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow()
            )
            db.add(setting)
            await db.commit()
            print("✅ Added last_checkin_sync setting")
        else:
            print("ℹ️  last_checkin_sync setting already exists")
        
        print("\n📊 Current sync settings:")
        result = await db.execute(
            select(AppSetting).where(
                AppSetting.key.in_(["last_crm_sync", "last_checkin_sync"])
            )
        )
        settings = result.scalars().all()
        for s in settings:
            print(f"   {s.key}: {s.value}")


if __name__ == "__main__":
    asyncio.run(add_checkin_sync_tracking())
