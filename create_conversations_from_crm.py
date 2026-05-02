"""
Create conversations from CRM comments so they appear in the inbox.
This creates basic conversations without full AI processing for speed.
"""
import asyncio
import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import CRMComment, Conversation, Message, Rep, Customer


async def create_conversations():
    """Create conversations from pending CRM comments."""
    async with AsyncSessionLocal() as db:
        # Get all pending comments with relationships
        result = await db.execute(
            select(CRMComment)
            .options(
                selectinload(CRMComment.rep),
                selectinload(CRMComment.customer)
            )
            .where(CRMComment.resolution_status == "pending")
            .where(CRMComment.conversation_id == None)  # Only comments without conversations
            .order_by(CRMComment.created_at.desc())
        )
        pending_comments = result.scalars().all()
        
        total = len(pending_comments)
        print(f"Found {total} CRM comments without conversations")
        
        if total == 0:
            print("All CRM comments already have conversations!")
            return
        
        created = 0
        skipped = 0
        
        for i, comment in enumerate(pending_comments, 1):
            try:
                rep = comment.rep
                customer = comment.customer
                
                if not rep:
                    print(f"  Skipping comment {comment.id}: No rep found")
                    skipped += 1
                    continue
                
                # Create conversation
                conv_topic = f"CRM: {customer.name}" if customer else f"CRM comment from {rep.name}"
                
                conv = Conversation(
                    id=str(uuid.uuid4()),
                    rep_id=rep.id,
                    customer_id=customer.id if customer else None,
                    topic=conv_topic,
                    pipeline_stage="Field visit follow-up",
                    objective=f"Follow up on: {comment.raw_text[:100]}...",
                    tactic="CRM-driven follow-up",
                    intel=comment.raw_text,
                    urgency="medium",
                    handler="ai",
                    crm_ref=comment.crm_comment_id,
                    created_at=comment.created_at or datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(conv)
                await db.flush()  # Get conv.id
                
                # Create initial message with the CRM comment
                msg = Message(
                    conversation_id=conv.id,
                    from_who="rep",
                    text=f"[CRM Visit Note]\n{comment.raw_text}",
                    ts=datetime.utcnow().strftime("%H:%M"),
                    date_label="today",
                    status="received",
                    is_read=False,
                    by_ai=False,
                    created_at=comment.created_at or datetime.utcnow(),
                )
                db.add(msg)
                
                # Link comment to conversation
                comment.conversation_id = conv.id
                comment.processed_summary = f"CRM visit note from {rep.name}"
                
                created += 1
                
                if created % 100 == 0:
                    await db.commit()
                    print(f"  Created {created}/{total} conversations...")
                    
            except Exception as e:
                print(f"  Error processing comment {comment.id}: {e}")
                skipped += 1
                continue
        
        # Final commit
        await db.commit()
        
        print(f"\n{'='*60}")
        print(f"Conversation creation complete!")
        print(f"  Successfully created: {created}")
        print(f"  Skipped: {skipped}")
        print(f"  Total: {total}")
        print(f"{'='*60}")
        print(f"\nAll CRM comments are now visible in the Inbox!")


if __name__ == "__main__":
    print("Creating conversations from CRM comments...")
    print("This will make all CRM comments visible in the inbox.")
    print("=" * 60)
    
    asyncio.run(create_conversations())
