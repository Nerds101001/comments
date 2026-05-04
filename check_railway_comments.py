"""Check what CRM comments exist in Railway database"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Railway DATABASE_URL
DATABASE_URL = "postgresql+asyncpg://postgres:VNdQGmDBLKxTaXAFBTXRmpqEAsxynprm@postgres.railway.internal:5432/railway"

async def check_comments():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Count total comments
        result = await session.execute(text("SELECT COUNT(*) FROM crm_comments"))
        total = result.scalar()
        print(f"Total CRM comments in database: {total}")
        
        # Get date range
        result = await session.execute(text("""
            SELECT 
                MIN(created_on) as earliest,
                MAX(created_on) as latest
            FROM crm_comments
        """))
        row = result.first()
        print(f"Date range: {row[0]} to {row[1]}")
        
        # Sample recent comments
        result = await session.execute(text("""
            SELECT comment_id, emp_code, comp_code, comment_text, created_on
            FROM crm_comments
            ORDER BY created_on DESC
            LIMIT 5
        """))
        print(f"\nRecent comments:")
        for row in result:
            print(f"  {row[4]}: {row[3][:50]}...")
    
    await engine.dispose()

asyncio.run(check_comments())
