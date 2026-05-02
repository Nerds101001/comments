"""
Add +91 country code to all 10-digit Indian phone numbers (automatic)
"""
import asyncio
import re
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import Rep

def clean_phone(phone):
    """Remove all non-digit characters"""
    if not phone:
        return ""
    return re.sub(r'\D', '', phone)

def needs_country_code(phone):
    """Check if phone number needs +91 prefix"""
    if not phone:
        return False
    
    cleaned = clean_phone(phone)
    
    # If exactly 10 digits and doesn't already start with 91
    if len(cleaned) == 10:
        return True
    
    return False

async def add_country_codes():
    print("=" * 80)
    print("ADDING +91 COUNTRY CODE TO 10-DIGIT NUMBERS")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # Get all active reps
        result = await db.execute(
            select(Rep)
            .where(Rep.is_active == True)
            .order_by(Rep.name)
        )
        reps = result.scalars().all()
        
        # Find and update numbers
        updated_count = 0
        updates = []
        
        for rep in reps:
            if needs_country_code(rep.phone):
                cleaned = clean_phone(rep.phone)
                old_phone = rep.phone
                new_phone = f"+91{cleaned}"
                rep.phone = new_phone
                updated_count += 1
                updates.append({
                    'name': rep.name,
                    'emp_code': rep.emp_code,
                    'old': old_phone,
                    'new': new_phone
                })
        
        if updated_count == 0:
            print("\n✅ All numbers already have country codes!")
            return
        
        print(f"\nUpdating {updated_count} phone numbers...\n")
        
        # Show updates
        print("Updated Numbers:")
        print("─" * 80)
        print(f"{'Name':<30} {'Emp Code':<12} {'Old':<20} {'New'}")
        print("─" * 80)
        
        for item in updates[:20]:  # Show first 20
            print(f"{item['name']:<30} {item['emp_code']:<12} {item['old']:<20} {item['new']}")
        
        if len(updates) > 20:
            print(f"... and {len(updates) - 20} more")
        
        # Commit changes
        await db.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Successfully updated {updated_count} phone numbers!")
        print("=" * 80)
        
        # Verify updates
        print("\nVerifying updates...")
        result = await db.execute(
            select(Rep)
            .where(Rep.is_active == True)
        )
        reps = result.scalars().all()
        
        # Count by format
        ten_digit = 0
        with_91 = 0
        other = 0
        no_phone = 0
        
        for rep in reps:
            if not rep.phone:
                no_phone += 1
            else:
                cleaned = clean_phone(rep.phone)
                if len(cleaned) == 10:
                    ten_digit += 1
                elif cleaned.startswith('91') and len(cleaned) == 12:
                    with_91 += 1
                else:
                    other += 1
        
        print("\nFinal Status:")
        print("─" * 80)
        print(f"10-digit numbers (no country code): {ten_digit}")
        print(f"12-digit numbers (with +91):         {with_91}")
        print(f"Other formats:                        {other}")
        print(f"No phone:                             {no_phone}")
        print("─" * 80)
        
        if ten_digit == 0:
            print("\n✅ All Indian numbers now have +91 country code!")
        
        # Export updated list
        print("\n" + "=" * 80)
        print("EXPORTING UPDATED LIST...")
        print("=" * 80)
        
        import csv
        with open('reps_with_country_codes.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Type', 'Name', 'Emp Code', 'Phone', 'Region'])
            
            for rep in reps:
                writer.writerow([
                    rep.rep_type or 'Unknown',
                    rep.name,
                    rep.emp_code,
                    rep.phone or '',
                    rep.region or ''
                ])
        
        print("✅ Exported to: reps_with_country_codes.csv")
        print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(add_country_codes())
