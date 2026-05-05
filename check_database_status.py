"""
Database Status Checker

This script checks:
1. Total comments in database
2. Comments by status (pending, resolved, etc.)
3. Recent comments
4. Last sync time
5. Pending comments details

Use this to diagnose why sync shows "0 0"
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models import CRMComment, AppSetting
from sqlalchemy import select, func
from datetime import datetime


async def main():
    print("=" * 60)
    print("Database Status Check")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        # 1. Count total comments
        print("1. Comment Counts:")
        total_result = await db.execute(select(func.count(CRMComment.id)))
        total = total_result.scalar()
        print(f"   Total comments: {total}")
        
        if total == 0:
            print("   ⚠️  No comments in database! Run sync first.")
            print()
            return
        
        # 2. Count by status
        print("\n2. Comments by Status:")
        for status in ["pending", "followup_sent", "resolved", "escalated"]:
            count_result = await db.execute(
                select(func.count(CRMComment.id))
                .where(CRMComment.resolution_status == status)
            )
            count = count_result.scalar()
            print(f"   {status:20s}: {count}")
        
        # 3. Last sync time
        print("\n3. Last Sync Time:")
        last_sync_result = await db.execute(
            select(AppSetting).where(AppSetting.key == "last_crm_sync")
        )
        last_sync_setting = last_sync_result.scalar_one_or_none()
        if last_sync_setting:
            print(f"   {last_sync_setting.value}")
        else:
            print("   Never synced")
        
        # 4. Recent comments
        print("\n4. Last 10 Comments:")
        recent_result = await db.execute(
            select(CRMComment)
            .order_by(CRMComment.created_at.desc())
            .limit(10)
        )
        recent = recent_result.scalars().all()
        
        for i, c in enumerate(recent, 1):
            print(f"   {i}. ID={c.id:4d} | Status={c.resolution_status:15s} | Date={c.created_at}")
            print(f"      Text: {c.raw_text[:60]}...")
        
        # 5. Pending comments details
        print("\n5. Pending Comments (first 5):")
        pending_result = await db.execute(
            select(CRMComment)
            .where(CRMComment.resolution_status == "pending")
            .order_by(CRMComment.created_at.asc())
            .limit(5)
        )
        pending = pending_result.scalars().all()
        
        if not pending:
            print("   ⚠️  No pending comments found!")
            print("   This is why process-all returns 0 0")
            print()
            print("   Possible reasons:")
            print("   - All comments already processed")
            print("   - Sync not fetching new comments")
            print("   - CRM API not returning data")
        else:
            for i, c in enumerate(pending, 1):
                print(f"   {i}. ID={c.id:4d} | Rep={c.rep_id} | Customer={c.customer_id}")
                print(f"      CRM ID: {c.crm_comment_id}")
                print(f"      Text: {c.raw_text[:80]}...")
                print()
        
        # 6. Date range of comments
        print("\n6. Comment Date Range:")
        oldest_result = await db.execute(
            select(CRMComment)
            .order_by(CRMComment.created_at.asc())
            .limit(1)
        )
        oldest = oldest_result.scalar_one_or_none()
        
        newest_result = await db.execute(
            select(CRMComment)
            .order_by(CRMComment.created_at.desc())
            .limit(1)
        )
        newest = newest_result.scalar_one_or_none()
        
        if oldest and newest:
            print(f"   Oldest: {oldest.created_at}")
            print(f"   Newest: {newest.created_at}")
            days = (newest.created_at - oldest.created_at).days
            print(f"   Span: {days} days")
        
        print()
        print("=" * 60)
        print("Diagnosis Complete")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
