"""
Add +91 country code to all 10-digit Indian phone numbers
"""
import asyncio
import re
from sqlalchemy import select, update
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
    
    # If starts with 91 and has 12 digits, already has country code
    if cleaned.startswith('91') and len(cleaned) == 12:
        return False
    
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
        
        # Find numbers that need updating
        to_update = []
        for rep in reps:
            if needs_country_code(rep.phone):
                cleaned = clean_phone(rep.phone)
                new_phone = f"+91{cleaned}"
                to_update.append({
                    'rep': rep,
                    'old': rep.phone,
                    'new': new_phone
                })
        
        print(f"\nFound {len(to_update)} numbers to update\n")
        
        if not to_update:
            print("✅ All numbers already have country codes!")
            return
        
        # Show what will be updated
        print("Numbers to be updated:")
        print("─" * 80)
        print(f"{'Name':<30} {'Emp Code':<12} {'Old':<20} {'New'}")
        print("─" * 80)
        
        for item in to_update[:20]:  # Show first 20
            print(f"{item['rep'].name:<30} {item['rep'].emp_code:<12} {item['old']:<20} {item['new']}")
        
        if len(to_update) > 20:
            print(f"... and {len(to_update) - 20} more")
        
        # Ask for confirmation
        print("\n" + "─" * 80)
        response = input(f"\nUpdate {len(to_update)} phone numbers? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("\n❌ Update cancelled")
            return
        
        # Update the database
        print("\n" + "─" * 80)
        print("Updating database...")
        print("─" * 80)
        
        updated_count = 0
        for item in to_update:
            rep = item['rep']
            rep.phone = item['new']
            updated_count += 1
            print(f"✅ Updated: {rep.name} ({rep.emp_code}) → {item['new']}")
        
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
            .order_by(Rep.name)
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
        else:
            print(f"\n⚠️  {ten_digit} numbers still need country code")

if __name__ == "__main__":
    asyncio.run(add_country_codes())
