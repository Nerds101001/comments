"""
Analyze phone number formats
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

def analyze_phone_format(phone):
    """Analyze phone number format"""
    if not phone:
        return "No phone", 0, ""
    
    cleaned = clean_phone(phone)
    digit_count = len(cleaned)
    
    # Determine country
    if cleaned.startswith('91') and digit_count == 12:
        return "India (with 91)", digit_count, cleaned
    elif cleaned.startswith('33') and digit_count == 11:
        return "France (with 33)", digit_count, cleaned
    elif cleaned.startswith('1') and digit_count == 11:
        return "USA/Canada (with 1)", digit_count, cleaned
    elif digit_count == 10:
        return "India (10 digits)", digit_count, cleaned
    else:
        return f"Other ({digit_count} digits)", digit_count, cleaned

async def analyze_phones():
    print("=" * 100)
    print("PHONE NUMBER FORMAT ANALYSIS")
    print("=" * 100)
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Rep)
            .where(Rep.is_active == True)
            .order_by(Rep.name)
        )
        reps = result.scalars().all()
        
        # Analyze all numbers
        analysis = []
        for rep in reps:
            format_type, digit_count, cleaned = analyze_phone_format(rep.phone)
            analysis.append({
                'name': rep.name,
                'emp_code': rep.emp_code,
                'rep_type': rep.rep_type,
                'original': rep.phone or "No phone",
                'cleaned': cleaned,
                'format': format_type,
                'digits': digit_count
            })
        
        # Group by format
        by_format = {}
        for item in analysis:
            fmt = item['format']
            if fmt not in by_format:
                by_format[fmt] = []
            by_format[fmt].append(item)
        
        # Display summary
        print(f"\n{'Format Type':<30} {'Count':<10} {'Percentage'}")
        print("─" * 100)
        for fmt, items in sorted(by_format.items(), key=lambda x: len(x[1]), reverse=True):
            pct = (len(items) / len(reps)) * 100
            print(f"{fmt:<30} {len(items):<10} {pct:.1f}%")
        
        # Show problematic numbers
        print(f"\n{'=' * 100}")
        print("NUMBERS THAT NEED ATTENTION")
        print("=" * 100)
        
        # Non-standard formats
        non_standard = [item for item in analysis if item['digits'] not in [0, 10, 11, 12]]
        if non_standard:
            print(f"\n❌ Non-standard format ({len(non_standard)}):")
            print(f"{'─' * 100}")
            print(f"{'Name':<30} {'Emp Code':<12} {'Original':<20} {'Cleaned':<15} {'Digits'}")
            print(f"{'─' * 100}")
            for item in non_standard:
                print(f"{item['name']:<30} {item['emp_code']:<12} {item['original']:<20} {item['cleaned']:<15} {item['digits']}")
        else:
            print("\n✅ All numbers are in standard format!")
        
        # Show all formats with examples
        print(f"\n{'=' * 100}")
        print("DETAILED BREAKDOWN BY FORMAT")
        print("=" * 100)
        
        for fmt, items in sorted(by_format.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n{'─' * 100}")
            print(f"📱 {fmt} ({len(items)} reps)")
            print(f"{'─' * 100}")
            print(f"{'Name':<30} {'Emp Code':<12} {'Original':<25} {'For WhatsApp'}")
            print(f"{'─' * 100}")
            
            # Show first 10 examples
            for item in items[:10]:
                wa_format = f"91{item['cleaned']}" if item['digits'] == 10 else item['cleaned']
                print(f"{item['name']:<30} {item['emp_code']:<12} {item['original']:<25} {wa_format}")
            
            if len(items) > 10:
                print(f"... and {len(items) - 10} more")
        
        # WhatsApp ready list
        print(f"\n{'=' * 100}")
        print("WHATSAPP READY NUMBERS (Properly Formatted)")
        print("=" * 100)
        
        whatsapp_ready = []
        for item in analysis:
            if item['digits'] == 10:
                # Indian number without country code
                whatsapp_ready.append(('91' + item['cleaned'], item['name'], item['emp_code']))
            elif item['digits'] == 12 and item['cleaned'].startswith('91'):
                # Indian number with country code
                whatsapp_ready.append((item['cleaned'], item['name'], item['emp_code']))
            elif item['digits'] == 11 and item['cleaned'].startswith('33'):
                # French number
                whatsapp_ready.append((item['cleaned'], item['name'], item['emp_code']))
            elif item['digits'] == 11 and item['cleaned'].startswith('1'):
                # US/Canada number
                whatsapp_ready.append((item['cleaned'], item['name'], item['emp_code']))
        
        print(f"\nTotal WhatsApp Ready: {len(whatsapp_ready)} out of {len(reps)} reps")
        print(f"\nFirst 20 numbers ready for WhatsApp:")
        print(f"{'─' * 100}")
        print(f"{'No.':<5} {'Name':<30} {'Emp Code':<12} {'WhatsApp Number'}")
        print(f"{'─' * 100}")
        
        for idx, (wa_num, name, emp_code) in enumerate(whatsapp_ready[:20], 1):
            print(f"{idx:<5} {name:<30} {emp_code:<12} {wa_num}")
        
        if len(whatsapp_ready) > 20:
            print(f"\n... and {len(whatsapp_ready) - 20} more")
        
        # Export WhatsApp ready list
        print(f"\n{'=' * 100}")
        print("EXPORTING WHATSAPP READY LIST...")
        print("=" * 100)
        
        import csv
        with open('whatsapp_ready_numbers.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['WhatsApp Number', 'Name', 'Emp Code', 'Rep Type'])
            
            for item in analysis:
                if item['digits'] == 10:
                    wa_num = '91' + item['cleaned']
                elif item['digits'] in [11, 12]:
                    wa_num = item['cleaned']
                else:
                    continue
                
                writer.writerow([wa_num, item['name'], item['emp_code'], item['rep_type']])
        
        print("✅ Exported to: whatsapp_ready_numbers.csv")
        print(f"   Total numbers: {len(whatsapp_ready)}")
        
        print(f"\n{'=' * 100}")

if __name__ == "__main__":
    asyncio.run(analyze_phones())
