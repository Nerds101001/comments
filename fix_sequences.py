"""
Fix PostgreSQL sequences after migration
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def fix_sequences():
    # Railway PostgreSQL PUBLIC URL
    railway_url = "postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@switchyard.proxy.rlwy.net:34827/railway"
    
    engine = create_async_engine(railway_url, echo=False)
    
    print("=" * 80)
    print("FIXING POSTGRESQL SEQUENCES")
    print("=" * 80)
    
    async with engine.begin() as conn:
        # Fix messages sequence
        print("\nFixing messages_id_seq...")
        await conn.execute(text(
            "SELECT setval('messages_id_seq', (SELECT MAX(id) FROM messages));"
        ))
        print("✅ messages_id_seq fixed")
        
        # Fix crm_comments sequence
        print("Fixing crm_comments_id_seq...")
        await conn.execute(text(
            "SELECT setval('crm_comments_id_seq', (SELECT MAX(id) FROM crm_comments));"
        ))
        print("✅ crm_comments_id_seq fixed")
        
        # Fix checkins sequence
        print("Fixing checkins_id_seq...")
        await conn.execute(text(
            "SELECT setval('checkins_id_seq', (SELECT MAX(id) FROM checkins));"
        ))
        print("✅ checkins_id_seq fixed")
        
        # Fix style_samples sequence
        print("Fixing style_samples_id_seq...")
        await conn.execute(text(
            "SELECT setval('style_samples_id_seq', COALESCE((SELECT MAX(id) FROM style_samples), 1));"
        ))
        print("✅ style_samples_id_seq fixed")
        
        # Fix style_profiles sequence
        print("Fixing style_profiles_id_seq...")
        await conn.execute(text(
            "SELECT setval('style_profiles_id_seq', COALESCE((SELECT MAX(id) FROM style_profiles), 1));"
        ))
        print("✅ style_profiles_id_seq fixed")
        
        # Fix senior_messages sequence (if exists)
        print("Fixing senior_messages_id_seq...")
        await conn.execute(text(
            "SELECT setval('senior_messages_id_seq', COALESCE((SELECT MAX(id) FROM senior_messages), 1));"
        ))
        print("✅ senior_messages_id_seq fixed")
    
    print("\n" + "=" * 80)
    print("✅ ALL SEQUENCES FIXED!")
    print("=" * 80)
    print("\nYour app should now work without errors.")
    print("Test at: https://web-production-fa001.up.railway.app")

if __name__ == "__main__":
    asyncio.run(fix_sequences())
