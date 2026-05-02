"""
Add API endpoint to get list of all reps for the dropdown selector
"""
import asyncio
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models import Rep, Conversation

async def get_rep_stats():
    """Get all reps with their conversation counts"""
    async with AsyncSessionLocal() as db:
        # Get all active reps with conversation counts
        result = await db.execute(
            select(
                Rep.id,
                Rep.name,
                Rep.emp_code,
                Rep.rep_type,
                Rep.avatar,
                Rep.color,
                func.count(Conversation.id).label('conv_count')
            )
            .outerjoin(Conversation, Conversation.rep_id == Rep.id)
            .where(Rep.is_active == True)
            .group_by(Rep.id, Rep.name, Rep.emp_code, Rep.rep_type, Rep.avatar, Rep.color)
            .order_by(Rep.name)
        )
        
        reps = result.all()
        
        print("Rep Statistics:")
        print("="*80)
        print(f"{'Name':<30} {'Type':<10} {'Emp Code':<10} {'Conversations':<15}")
        print("-"*80)
        
        by_type = {}
        for rep in reps:
            print(f"{rep.name:<30} {rep.rep_type:<10} {rep.emp_code:<10} {rep.conv_count:<15}")
            
            if rep.rep_type not in by_type:
                by_type[rep.rep_type] = {'count': 0, 'convs': 0}
            by_type[rep.rep_type]['count'] += 1
            by_type[rep.rep_type]['convs'] += rep.conv_count
        
        print("\n" + "="*80)
        print("Summary by Type:")
        print("-"*80)
        for rep_type, stats in sorted(by_type.items()):
            print(f"{rep_type:<10} {stats['count']:>3} reps, {stats['convs']:>5} conversations")
        
        print("\n" + "="*80)
        print(f"Total: {len(reps)} reps, {sum(r.conv_count for r in reps)} conversations")

if __name__ == "__main__":
    asyncio.run(get_rep_stats())
