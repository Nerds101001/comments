"""
Better linking strategy for check-ins to comments
"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("Analyzing date formats...")

# Check comment date format
cursor.execute('SELECT comment_date FROM crm_comments WHERE comment_date IS NOT NULL LIMIT 5')
print("\nComment dates (sample):")
for row in cursor.fetchall():
    print(f"  {row[0]}")

# Check checkin date format
cursor.execute('SELECT checkin_date FROM checkins LIMIT 5')
print("\nCheck-in dates (sample):")
for row in cursor.fetchall():
    print(f"  {row[0]}")

print("\n" + "="*60)
print("Linking check-ins to comments...")
print("="*60)

# Strategy: Link based on emp_code, comp_code, and same date
# We'll try to match dates even if formats differ
linked = 0
cursor.execute('''
    SELECT id, emp_code, comp_code, checkin_date 
    FROM checkins 
    WHERE comp_code IS NOT NULL AND comp_code != '0'
    LIMIT 1000
''')
checkins = cursor.fetchall()

for checkin_id, emp_code, comp_code, checkin_date in checkins:
    # Try to find matching comment
    cursor.execute('''
        SELECT id FROM crm_comments
        WHERE crm_emp_code = ? 
        AND crm_comp_code = ?
        AND comment_date = ?
        LIMIT 1
    ''', (emp_code, comp_code, checkin_date))
    
    comment = cursor.fetchone()
    if comment:
        cursor.execute('UPDATE checkins SET comment_id = ? WHERE id = ?', (comment[0], checkin_id))
        linked += 1

conn.commit()
print(f"\n✅ Linked {linked} check-ins to comments")

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
    SELECT c.emp_code, c.emp_name, c.comp_name, c.checkin_date, cc.raw_text
    FROM checkins c
    JOIN crm_comments cc ON c.comment_id = cc.id
    LIMIT 3
''')
for row in cursor.fetchall():
    print(f"\n  Rep: {row[1]} ({row[0]})")
    print(f"  Customer: {row[2]}")
    print(f"  Date: {row[3]}")
    print(f"  Comment: {row[4][:100]}...")

conn.close()
