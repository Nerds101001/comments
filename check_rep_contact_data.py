#!/usr/bin/env python3
"""
Check if all reps have real phone numbers from CRM
"""
import sqlite3
import json

def check_rep_data():
    conn = sqlite3.connect('hitech_sales.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all reps
    cursor.execute("""
        SELECT id, name, emp_code, phone, rep_type, region, is_active
        FROM reps
        ORDER BY rep_type, name
    """)
    
    reps = cursor.fetchall()
    
    print("=" * 100)
    print("REP CONTACT DATA VERIFICATION")
    print("=" * 100)
    print(f"\nTotal Reps: {len(reps)}\n")
    
    # Group by type
    by_type = {}
    missing_phone = []
    has_phone = []
    inactive_reps = []
    
    for rep in reps:
        rep_type = rep['rep_type'] or 'unknown'
        if rep_type not in by_type:
            by_type[rep_type] = []
        by_type[rep_type].append(rep)
        
        if not rep['is_active']:
            inactive_reps.append(rep)
            continue
            
        has_phone_data = rep['phone'] and rep['phone'].strip() and rep['phone'] != 'NULL' and rep['phone'] != 'None'
        
        if not has_phone_data:
            missing_phone.append(rep)
        else:
            has_phone.append(rep)
    
    # Summary by type
    print("SUMMARY BY TYPE:")
    print("-" * 100)
    for rep_type, reps_list in sorted(by_type.items()):
        active_count = len([r for r in reps_list if r['is_active']])
        print(f"\n{rep_type.upper()}: {len(reps_list)} reps ({active_count} active)")
        for rep in reps_list[:5]:  # Show first 5 of each type
            phone_status = "✅" if rep['phone'] and rep['phone'].strip() and rep['phone'] != 'NULL' else "❌"
            active_status = "🟢" if rep['is_active'] else "⚫"
            print(f"  {active_status} {phone_status} {rep['name']:<35} | EMP: {rep['emp_code']:<8} | Phone: {rep['phone'] or 'MISSING':<20} | Region: {rep['region'] or 'N/A'}")
        if len(reps_list) > 5:
            print(f"  ... and {len(reps_list) - 5} more")
    
    # Overall statistics
    print("\n" + "=" * 100)
    print("OVERALL STATISTICS:")
    print("-" * 100)
    active_reps = [r for r in reps if r['is_active']]
    print(f"Total reps in database:        {len(reps)}")
    print(f"Active reps:                   {len(active_reps)} ({len(active_reps)/len(reps)*100:.1f}%)")
    print(f"Inactive reps:                 {len(inactive_reps)} ({len(inactive_reps)/len(reps)*100:.1f}%)")
    print(f"✅ Active reps with phone:     {len(has_phone)} ({len(has_phone)/len(active_reps)*100:.1f}% of active)")
    print(f"❌ Active reps missing phone:  {len(missing_phone)} ({len(missing_phone)/len(active_reps)*100:.1f}% of active)")
    
    # Show reps missing contact info
    if missing_phone:
        print("\n" + "=" * 100)
        print("⚠️  ACTIVE REPS MISSING PHONE NUMBERS:")
        print("-" * 100)
        for rep in missing_phone[:15]:  # Show first 15
            print(f"  {rep['name']:<35} | EMP: {rep['emp_code']:<8} | Type: {rep['rep_type']:<10} | Region: {rep['region'] or 'N/A'}")
        if len(missing_phone) > 15:
            print(f"  ... and {len(missing_phone) - 15} more")
    
    # Check sample of complete records
    print("\n" + "=" * 100)
    print("✅ SAMPLE OF ACTIVE REPS WITH PHONE NUMBERS (ready for AI nudges):")
    print("-" * 100)
    for rep in has_phone[:15]:
        print(f"  {rep['name']:<35} | EMP: {rep['emp_code']:<8} | Type: {rep['rep_type']:<10}")
        print(f"    📞 Phone: {rep['phone']}")
        print()
    
    if len(has_phone) > 15:
        print(f"  ... and {len(has_phone) - 15} more complete records")
    
    # Check CRM sync status
    print("\n" + "=" * 100)
    print("CRM SYNC STATUS:")
    print("-" * 100)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN is_active = 1 THEN 1 END) as active,
            COUNT(CASE WHEN phone IS NOT NULL AND phone != '' AND phone != 'NULL' AND is_active = 1 THEN 1 END) as active_with_phone
        FROM reps
    """)
    
    stats = cursor.fetchone()
    print(f"Total reps in database:              {stats['total']}")
    print(f"Active reps:                         {stats['active']} ({stats['active']/stats['total']*100:.1f}%)")
    print(f"Active reps with phone (ready):      {stats['active_with_phone']} ({stats['active_with_phone']/stats['active']*100:.1f}% of active)")
    
    # Check if data looks like real data or dummy data
    print("\n" + "=" * 100)
    print("DATA QUALITY CHECK:")
    print("-" * 100)
    
    cursor.execute("""
        SELECT phone, COUNT(*) as count, GROUP_CONCAT(name, ', ') as names
        FROM reps
        WHERE phone IS NOT NULL AND phone != '' AND phone != 'NULL' AND is_active = 1
        GROUP BY phone
        HAVING count > 1
        ORDER BY count DESC
        LIMIT 5
    """)
    
    duplicates = cursor.fetchall()
    if duplicates:
        print("⚠️  DUPLICATE PHONE NUMBERS FOUND (possible dummy data):")
        for dup in duplicates:
            names = dup['names'][:80] + '...' if len(dup['names']) > 80 else dup['names']
            print(f"  Phone: {dup['phone']} used by {dup['count']} reps: {names}")
    else:
        print("✅ No duplicate phone numbers - data looks unique and real")
    
    # Check phone number format
    cursor.execute("""
        SELECT name, phone, emp_code
        FROM reps
        WHERE phone IS NOT NULL AND phone != '' AND phone != 'NULL' AND is_active = 1
        LIMIT 10
    """)
    
    samples = cursor.fetchall()
    print("\nSAMPLE PHONE NUMBER FORMATS:")
    for sample in samples:
        phone_len = len(sample['phone']) if sample['phone'] else 0
        # Check if it looks like Indian mobile number
        is_indian = sample['phone'].startswith('91') if sample['phone'] else False
        format_check = "✅ Indian format" if is_indian and phone_len >= 12 else "⚠️  Check format"
        print(f"  {sample['name']:<35} | {sample['phone']:<20} (len: {phone_len:2d}) {format_check}")
    
    # Check CRM comments table for additional contact info
    print("\n" + "=" * 100)
    print("CHECKING CRM DATA SOURCE:")
    print("-" * 100)
    
    try:
        cursor.execute("SELECT COUNT(*) as count FROM crm_comments")
        crm_count = cursor.fetchone()['count']
        print(f"✅ CRM comments in database: {crm_count}")
        
        cursor.execute("""
            SELECT created_at 
            FROM crm_comments 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        latest = cursor.fetchone()
        if latest:
            print(f"   Latest CRM data: {latest['created_at']}")
    except:
        print("⚠️  CRM comments table not found or empty")
    
    conn.close()
    
    print("\n" + "=" * 100)
    print("RECOMMENDATION:")
    print("-" * 100)
    if len(has_phone) == len(active_reps):
        print("✅ ALL ACTIVE REPS HAVE PHONE NUMBERS - Ready to send AI nudges via WhatsApp!")
        print(f"   {len(has_phone)} reps can receive AI nudges")
    elif len(has_phone) > len(active_reps) * 0.8:
        print(f"⚠️  {len(has_phone)} active reps have phone numbers ({len(has_phone)/len(active_reps)*100:.1f}%)")
        print(f"   {len(missing_phone)} active reps need phone numbers updated in CRM")
        print(f"   AI nudges can be sent to {len(has_phone)} reps with phone numbers")
        print("\n   ACTION: Update missing phone numbers in CRM, then run: POST /api/crm/sync")
    else:
        print(f"❌ Only {len(has_phone)} active reps have phone numbers ({len(has_phone)/len(active_reps)*100:.1f}%)")
        print("   URGENT: Update phone numbers in CRM before sending AI nudges")
        print("   Run CRM sync to fetch latest data: POST /api/crm/sync")
    
    print("\n" + "=" * 100)
    print("NOTE: Email addresses are not currently stored in the reps table.")
    print("      If needed, add an 'email' column to the reps table and update CRM sync.")
    print("=" * 100)

if __name__ == "__main__":
    check_rep_data()
