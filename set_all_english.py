"""
Set all reps to use english_only language (no Hindi)
"""
import asyncio
from sqlalchemy import select, update
from app.database import AsyncSessionLocal
from app.models import Rep

async def set_all_english():
    async with AsyncSessionLocal() as db:
        # Update all reps to english_only
        result = await db.execute(
            update(Rep)
            .values(language="english_only")
        )
        
        await db.commit()
        
        # Verify
        reps_result = await db.execute(select(Rep))
        reps = reps_result.scalars().all()
        
        print(f"✅ Updated {len(reps)} reps to english_only language")
        print("\nSample reps:")
        for rep in reps[:5]:
            print(f"  - {rep.name}: {rep.language}")

if __name__ == "__main__":
    print("Setting all reps to English only (no Hindi)...")
    print("=" * 60)
    asyncio.run(set_all_english())
    print("\n✅ All AI responses will now be in pure English!")
