"""
Quick Diagnostic Script

Runs all diagnostics in one go to identify issues quickly.

Usage:
    python quick_diagnostic.py
"""
import asyncio
import httpx
from app.database import AsyncSessionLocal
from app.models import CRMComment, AppSetting
from sqlalchemy import select, func
from datetime import datetime


async def check_database():
    """Check database status"""
    print("=" * 70)
    print("1. DATABASE STATUS")
    print("=" * 70)
    
    async with AsyncSessionLocal() as db:
        # Total comments
        total_result = await db.execute(select(func.count(CRMComment.id)))
        total = total_result.scalar()
        print(f"Total comments: {total:,}")
        
        if total == 0:
            print("⚠️  No comments in database!")
            print("   Action: Run sync with --hours 720 to fetch last 30 days")
            return False
        
        # By status
        print("\nBy status:")
        pending_count = 0
        for status in ["pending", "followup_sent", "resolved", "escalated"]:
            count_result = await db.execute(
                select(func.count(CRMComment.id))
                .where(CRMComment.resolution_status == status)
            )
            count = count_result.scalar()
            print(f"  {status:20s}: {count:,}")
            if status == "pending":
                pending_count = count
        
        # Last sync
        last_sync_result = await db.execute(
            select(AppSetting).where(AppSetting.key == "last_crm_sync")
        )
        last_sync_setting = last_sync_result.scalar_one_or_none()
        print(f"\nLast sync: {last_sync_setting.value if last_sync_setting else 'Never'}")
        
        if pending_count == 0:
            print("\n⚠️  No pending comments!")
            print("   This is why you see '0 0' when processing")
            print("   Action: Run sync or reset comments for testing")
            return False
        
        print(f"\n✅ {pending_count:,} pending comments ready to process")
        return True


async def check_api_connections():
    """Check API connections"""
    print("\n" + "=" * 70)
    print("2. API CONNECTIONS")
    print("=" * 70)
    
    api_base = "http://localhost:8002"
    
    async with httpx.AsyncClient(timeout=10) as client:
        # CRM
        try:
            resp = await client.get(f"{api_base}/api/crm/status")
            data = resp.json()
            if data.get("status") == "connected":
                print("✅ CRM: Connected")
            else:
                print(f"❌ CRM: {data.get('status')}")
        except Exception as e:
            print(f"❌ CRM: Error - {e}")
        
        # AI
        try:
            resp = await client.post(f"{api_base}/api/settings/test/ai")
            data = resp.json()
            if data.get("status") == "connected":
                print(f"✅ AI: {data.get('message')}")
            else:
                print(f"❌ AI: {data.get('message')}")
        except Exception as e:
            print(f"❌ AI: Error - {e}")
        
        # SMTP
        try:
            resp = await client.post(f"{api_base}/api/settings/test/smtp")
            data = resp.json()
            if data.get("status") == "connected":
                print(f"✅ SMTP: {data.get('message')}")
            else:
                print(f"❌ SMTP: {data.get('message')}")
        except Exception as e:
            print(f"❌ SMTP: Error - {e}")
        
        # WhatsApp
        try:
            resp = await client.post(f"{api_base}/api/settings/test/whatsapp")
            data = resp.json()
            if data.get("status") == "connected":
                print("✅ WhatsApp: Connected")
            else:
                print(f"⚠️  WhatsApp: {data.get('status')}")
        except Exception as e:
            print(f"❌ WhatsApp: Error - {e}")


async def check_recent_activity():
    """Check recent activity"""
    print("\n" + "=" * 70)
    print("3. RECENT ACTIVITY")
    print("=" * 70)
    
    async with AsyncSessionLocal() as db:
        # Recent comments
        recent_result = await db.execute(
            select(CRMComment)
            .order_by(CRMComment.created_at.desc())
            .limit(5)
        )
        recent = recent_result.scalars().all()
        
        print("\nLast 5 comments:")
        for i, c in enumerate(recent, 1):
            print(f"  {i}. ID={c.id:4d} | Status={c.resolution_status:15s}")
            print(f"     Date: {c.created_at}")
            print(f"     Text: {c.raw_text[:60]}...")
        
        # Pending sample
        pending_result = await db.execute(
            select(CRMComment)
            .where(CRMComment.resolution_status == "pending")
            .order_by(CRMComment.created_at.asc())
            .limit(3)
        )
        pending = pending_result.scalars().all()
        
        if pending:
            print("\nNext 3 pending to process:")
            for i, c in enumerate(pending, 1):
                print(f"  {i}. ID={c.id:4d} | Rep={c.rep_id}")
                print(f"     Text: {c.raw_text[:60]}...")


def print_recommendations():
    """Print recommendations"""
    print("\n" + "=" * 70)
    print("4. RECOMMENDATIONS")
    print("=" * 70)
    print()
    print("Based on the diagnostics above:")
    print()
    print("If you see '❌ SMTP' error:")
    print("  → The SSL context fix has been applied")
    print("  → Restart your application: railway restart (or restart locally)")
    print("  → Test again via Settings UI")
    print()
    print("If you see '⚠️  No pending comments':")
    print("  → Run: python manual_sync_improved.py --hours 720")
    print("  → This will sync last 30 days from CRM")
    print()
    print("If you see '❌ CRM' error:")
    print("  → Check CRM credentials in .env or Railway")
    print("  → Verify CRM_USERNAME and CRM_PASSWORD are correct")
    print()
    print("If you see '❌ AI' error:")
    print("  → Check AI_API_KEY in .env or Railway")
    print("  → Verify the API key is valid")
    print()
    print("To process pending comments:")
    print("  → Run: python manual_sync_improved.py")
    print()
    print("For more help:")
    print("  → See TROUBLESHOOTING_GUIDE.md")
    print("  → See FIXES_APPLIED_SUMMARY.md")
    print()


async def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "QUICK DIAGNOSTIC" + " " * 32 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    try:
        # Check database
        has_pending = await check_database()
        
        # Check API connections
        await check_api_connections()
        
        # Check recent activity
        if has_pending:
            await check_recent_activity()
        
        # Print recommendations
        print_recommendations()
        
    except Exception as e:
        print(f"\n❌ Error running diagnostics: {e}")
        print("\nMake sure:")
        print("  1. Application is running (python -m uvicorn app.main:app)")
        print("  2. Database exists (hitech_sales.db)")
        print("  3. You're in the project root directory")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
