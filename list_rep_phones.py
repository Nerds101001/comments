"""
List all representatives with their phone numbers
"""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import Rep

async def list_rep_phones():
    print("=" * 80)
    print("ALL REPRESENTATIVES - PHONE NUMBERS")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # Get all active reps
        result = await db.execute(
            select(Rep)
            .where(Rep.is_active == True)
            .order_by(Rep.rep_type, Rep.name)
        )
        reps = result.scalars().all()
        
        print(f"\nTotal Active Reps: {len(reps)}\n")
        
        # Group by rep type
        by_type = {}
        for rep in reps:
            rep_type = rep.rep_type or "Unknown"
            if rep_type not in by_type:
                by_type[rep_type] = []
            by_type[rep_type].append(rep)
        
        # Display by type
        for rep_type, type_reps in sorted(by_type.items()):
            print(f"\n{'─' * 80}")
            print(f"📋 {rep_type.upper()} REPS ({len(type_reps)})")
            print(f"{'─' * 80}")
            print(f"{'No.':<4} {'Name':<30} {'Emp Code':<10} {'Phone':<15} {'Region':<15}")
            print(f"{'─' * 80}")
            
            for idx, rep in enumerate(type_reps, 1):
                phone = rep.phone or "No phone"
                region = rep.region or "N/A"
                print(f"{idx:<4} {rep.name:<30} {rep.emp_code:<10} {phone:<15} {region:<15}")
        
        # Summary
        print(f"\n{'=' * 80}")
        print("SUMMARY BY TYPE")
        print(f"{'=' * 80}")
        for rep_type, type_reps in sorted(by_type.items()):
            with_phone = sum(1 for r in type_reps if r.phone)
            print(f"{rep_type:<15} Total: {len(type_reps):<3} | With Phone: {with_phone:<3} | Without Phone: {len(type_reps) - with_phone}")
        
        # Export to CSV
        print(f"\n{'=' * 80}")
        print("EXPORTING TO CSV...")
        print(f"{'=' * 80}")
        
        import csv
        with open('rep_phone_list.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Type', 'Name', 'Emp Code', 'Phone', 'Region', 'Role'])
            
            for rep in reps:
                writer.writerow([
                    rep.rep_type or 'Unknown',
                    rep.name,
                    rep.emp_code,
                    rep.phone or '',
                    rep.region or '',
                    rep.role or ''
                ])
        
        print("✅ Exported to: rep_phone_list.csv")
        
        # WhatsApp ready numbers
        print(f"\n{'=' * 80}")
        print("WHATSAPP READY NUMBERS (With Phone)")
        print(f"{'=' * 80}")
        
        whatsapp_ready = [r for r in reps if r.phone]
        print(f"\nTotal: {len(whatsapp_ready)} reps have phone numbers\n")
        
        # Show first 20 for WhatsApp
        print("First 20 numbers for WhatsApp testing:")
        print(f"{'─' * 80}")
        for idx, rep in enumerate(whatsapp_ready[:20], 1):
            # Format for WhatsApp (remove + and spaces)
            wa_number = rep.phone.replace('+', '').replace(' ', '').replace('-', '')
            print(f"{idx:<3} {rep.name:<30} {wa_number}")
        
        if len(whatsapp_ready) > 20:
            print(f"\n... and {len(whatsapp_ready) - 20} more")
        
        print(f"\n{'=' * 80}")

if __name__ == "__main__":
    asyncio.run(list_rep_phones())
