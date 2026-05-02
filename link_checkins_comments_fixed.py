"""
Link check-ins to comments with date format conversion
"""
import sqlite3
from datetime import datetime

def convert_date_format(date_str, from_format, to_format):
    """Convert date from one format to another"""
    try:
        if from_format == "MM/DD/YYYY HH:MM:SS":
            # Parse: 04/30/2026 13:52:14
            dt = datetime.strptime(date_str.split()[0], "%m/%d/%Y")
            if to_format == "DD-MM-YYYY":
                return dt.strftime("%d-%m-%Y")
        elif from_format == "DD-MM-YYYY":
            # Parse: 01-04-2026
            dt = datetime.strptime(date_str, "%d-%m-%Y")
            if to_format == "MM/DD/YYYY":
                return dt.strftime("%m/%d/%Y")
    except:
        return None
    return None

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("Linking check-ins to comments with date conversion...")
print("="*60)

# Get all check-ins
cursor.execute('''
    SELECT id, emp_code, comp_code, checkin_date 
    FROM checkins 
    WHERE comp_code IS NOT NULL AND comp_code != '0' AND comp_code != ''
''')
checkins = cursor.fetchall()

linked = 0
not_found = 0

for checkin_id, emp_code, comp_code, checkin_date in checkins:
    # Convert checkin date from DD-MM-YYYY to MM/DD/YYYY for matching
    converted_date = convert_date_format(checkin_date, "DD-MM-YYYY", "MM/DD/YYYY")
    
    if not converted_date:
        continue
    
    # Try to find matching comment (comment_date starts with MM/DD/YYYY)
    cursor.execute('''
        SELECT id FROM crm_comments
        WHERE crm_emp_code = ? 
        AND crm_comp_code = ?
        AND comment_date LIKE ?
        LIMIT 1
    ''', (emp_code, comp_code, f"{converted_date}%"))
    
    comment = cursor.fetchone()
    if comment:
        cursor.execute('UPDATE checkins SET comment_id = ? WHERE id = ?', (comment[0], checkin_id))
        linked += 1
    else:
        not_found += 1
    
    if (linked + not_found) % 500 == 0:
        print(f"  Processed {linked + not_found} check-ins... (linked: {linked})")

conn.commit()
print(f"\n✅ Processed {linked + not_found} check-ins")
print(f"   Linked: {linked}")
print(f"   Not found: {not_found}")

# Verification
cursor.execute('SELECT COUNT(*) FROM checkins WHERE comment_id IS NOT NULL')
total_linked = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM checkins')
total_checkins = cursor.fetchone()[0]

print(f"\nFinal Status:")
print(f"  Total check-ins: {total_checkins}")
print(f"  Linked to comments: {total_linked}")
print(f"  Not linked: {total_checkins - total_linked}")
print(f"  Link rate: {(total_linked/total_checkins*100):.1f}%")

# Show some examples
print("\nExample linked check-ins:")
cursor.execute('''
    SELECT c.emp_code, c.emp_name, c.comp_name, c.checkin_date, c.checkin_time, cc.raw_text
    FROM checkins c
    JOIN crm_comments cc ON c.comment_id = cc.id
    LIMIT 5
''')
for row in cursor.fetchall():
    print(f"\n  Rep: {row[1]} ({row[0]})")
    print(f"  Customer: {row[2]}")
    print(f"  Check-in: {row[3]} at {row[4]}")
    print(f"  Comment: {row[5][:80]}...")

conn.close()
print("\n✅ Done!")
