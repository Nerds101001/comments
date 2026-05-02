"""
Process all pending CRM comments to create conversations for the inbox.
This will make all CRM comments visible in the frontend inbox with AI analysis.
"""
import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models import CRMComment
from app.services import ai_brain


async def process_all_comments():
    """Process all pending CRM comments in batches."""
    async with async_session_maker() as db:
        # Get all pending comments
        result = await db.execute(
            select(CRMComment)
            .where(CRMComment.resolution_status == "pending")
            .order_by(CRMComment.created_at.desc())
        )
        pending_comments = result.scalars().all()
        
        total = len(pending_comments)
        print(f"Found {total} pending CRM comments to process")
        
        if total == 0:
            print("No pending comments to process!")
            return
        
        # Process in batches
        batch_size = 100
        processed = 0
        errors = 0
        
        for i in range(0, total, batch_size):
            batch = pending_comments[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} comments)...")
            
            for comment in batch:
                try:
                    # Import here to avoid circular imports
                    from app.api.crm import process_comment
                    
                    # Process the comment (creates conversation, generates follow-up)
                    await process_comment(comment.id, db)
                    processed += 1
                    
                    if processed % 10 == 0:
                        print(f"  Processed {processed}/{total}...")
                        
                except Exception as e:
                    print(f"  Error processing comment {comment.id}: {e}")
                    errors += 1
                    continue
        
        print(f"\n{'='*60}")
        print(f"Processing complete!")
        print(f"  Successfully processed: {processed}")
        print(f"  Errors: {errors}")
        print(f"  Total: {total}")
        print(f"{'='*60}")


if __name__ == "__main__":
    print("Starting CRM comment processing...")
    print("This will create conversations for all pending CRM comments.")
    print("=" * 60)
    
    asyncio.run(process_all_comments())
