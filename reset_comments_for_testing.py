"""
Reset Comments for Testing

This script resets comment statuses back to "pending" so you can test
the processing pipeline again.

Usage:
    python reset_comments_for_testing.py           # Reset last 50 comments
    python reset_comments_for_testing.py --all     # Reset ALL comments
    python reset_comments_for_testing.py --count 100  # Reset last 100 comments

⚠️  WARNING: This will reset processed comments back to pending!
"""
import asyncio
import argparse
from app.database import AsyncSessionLocal
from app.models import CRMComment
from sqlalchemy import select


async def reset_comments(count: int = 50, reset_all: bool = False):
    print("=" * 60)
    print("Reset Comments for Testing")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        if reset_all:
            print("⚠️  Resetting ALL comments to pending...")
            result = await db.execute(select(CRMComment))
            comments = result.scalars().all()
        else:
            print(f"Resetting last {count} comments to pending...")
            result = await db.execute(
                select(CRMComment)
                .order_by(CRMComment.created_at.desc())
                .limit(count)
            )
            comments = result.scalars().all()
        
        if not comments:
            print("No comments found in database!")
            return
        
        print(f"Found {len(comments)} comments to reset")
        print()
        
        # Show what will be reset
        print("Status breakdown before reset:")
        status_counts = {}
        for c in comments:
            status_counts[c.resolution_status] = status_counts.get(c.resolution_status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"  {status:20s}: {count}")
        print()
        
        # Confirm
        if reset_all:
            confirm = input("⚠️  Are you sure you want to reset ALL comments? (yes/no): ")
        else:
            confirm = input(f"Reset {len(comments)} comments to pending? (yes/no): ")
        
        if confirm.lower() != "yes":
            print("Cancelled.")
            return
        
        # Reset
        for c in comments:
            c.resolution_status = "pending"
            c.followup_sent = False
            c.followup_sent_at = None
            c.processed_summary = None
            c.followup_question = None
            c.conversation_id = None
        
        await db.commit()
        
        print()
        print(f"✅ Reset {len(comments)} comments to pending")
        print()
        print("You can now run manual_sync_and_process.py to process them again")
        print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset comments for testing")
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of recent comments to reset (default: 50)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Reset ALL comments (use with caution!)"
    )
    args = parser.parse_args()
    
    asyncio.run(reset_comments(count=args.count, reset_all=args.all))
