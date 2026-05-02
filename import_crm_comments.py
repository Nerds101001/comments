"""Import CRM comments from JSON file into database"""
import asyncio
import json
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, init_db
from app.models import CRMComment, Rep, Customer

async def import_comments():
    print("="*80)
    print("IMPORTING CRM COMMENTS TO DATABASE")
    print("="*80)
    
    # Initialize database
    await init_db()
    
    # Load JSON file
    print("\nLoading crm_comments_full.json...")
    with open("crm_comments_full.json", "r", encoding="utf-8") as f:
        comments_data = json.load(f)
    
    print(f"✓ Loaded {len(comments_data)} comments from JSON")
    
    async with AsyncSessionLocal() as db:
        # Load all reps for mapping
        reps_result = await db.execute(select(Rep))
        all_reps = reps_result.scalars().all()
        reps_by_emp = {r.emp_code: r for r in all_reps}
        print(f"✓ Loaded {len(reps_by_emp)} reps from database")
        
        # Load all customers for mapping
        custs_result = await db.execute(select(Customer))
        all_custs = custs_result.scalars().all()
        custs_by_code = {c.comp_code: c for c in all_custs}
        print(f"✓ Loaded {len(custs_by_code)} customers from database")
        
        # Import comments
        imported = 0
        skipped = 0
        
        print(f"\nImporting comments...")
        for i, comment_data in enumerate(comments_data, 1):
            if i % 1000 == 0:
                print(f"  Processed {i}/{len(comments_data)}...")
            
            # Extract fields
            comp_code = str(comment_data.get("COMP_CODE") or "")
            emp_code = str(comment_data.get("EMP_CODE") or "")
            comment_text = comment_data.get("Comment") or comment_data.get("comment") or ""
            created_on = comment_data.get("CreatedOn") or comment_data.get("createdOn") or ""
            
            if not comment_text or len(comment_text.strip()) < 5:
                skipped += 1
                continue
            
            # Map to rep and customer
            rep = reps_by_emp.get(emp_code)
            customer = custs_by_code.get(comp_code)
            
            # Create CRM comment
            crm_comment = CRMComment(
                crm_comment_id=None,  # No unique ID in the data
                rep_id=rep.id if rep else None,
                customer_id=customer.id if customer else None,
                crm_emp_code=emp_code,
                crm_comp_code=comp_code,
                raw_text=comment_text.strip(),
                comment_date=created_on,
                processed_summary=None,
                followup_question=None,
                followup_sent=False,
                resolution_status="pending",
                created_at=datetime.utcnow(),
            )
            
            db.add(crm_comment)
            imported += 1
        
        # Commit all
        print(f"\nCommitting to database...")
        await db.commit()
        
        print(f"\n{'='*80}")
        print(f"IMPORT COMPLETE")
        print(f"{'='*80}")
        print(f"✓ Imported: {imported} comments")
        print(f"⚠ Skipped: {skipped} comments (empty or too short)")
        print(f"Total in database: {imported}")
        
        # Verify
        count_result = await db.execute(select(CRMComment))
        final_count = len(count_result.scalars().all())
        print(f"\n✓ Verification: {final_count} comments now in database")


if __name__ == "__main__":
    asyncio.run(import_comments())
