"""
Add rep_type field and link check-ins to comments
"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("Step 1: Adding rep_type column to reps table...")
try:
    cursor.execute('ALTER TABLE reps ADD COLUMN rep_type TEXT DEFAULT "sales"')
    print("✅ Added rep_type column")
except Exception as e:
    print(f"⚠️  Column might already exist: {e}")

print("\nStep 2: Updating rep_type based on role...")
# Update rep_type based on role
cursor.execute('''
    UPDATE reps 
    SET rep_type = CASE 
        WHEN role LIKE '%CCARE%' OR role LIKE '%Customer Care%' THEN 'ccare'
        WHEN role LIKE '%NEW BIZ%' OR role LIKE '%Business%' THEN 'newbiz'
        WHEN role LIKE '%SALES%' OR role LIKE '%Sales%' THEN 'sales'
        WHEN role LIKE '%ADMIN%' THEN 'admin'
        WHEN role LIKE '%FINANCE%' THEN 'finance'
        ELSE 'sales'
    END
''')
print(f"✅ Updated {cursor.rowcount} reps with rep_type")

print("\nStep 3: Adding comment_id to checkins table...")
try:
    cursor.execute('ALTER TABLE checkins ADD COLUMN comment_id INTEGER')
    cursor.execute('CREATE INDEX idx_checkins_comment_id ON checkins(comment_id)')
    print("✅ Added comment_id column and index")
except Exception as e:
    print(f"⚠️  Column might already exist: {e}")

print("\nStep 4: Linking check-ins to comments...")
# Link check-ins to comments based on emp_code, comp_code, and date proximity
cursor.execute('''
    UPDATE checkins
    SET comment_id = (
        SELECT crm_comments.id
        FROM crm_comments
        WHERE crm_comments.crm_emp_code = checkins.emp_code
        AND crm_comments.crm_comp_code = checkins.comp_code
        AND crm_comments.comment_date = checkins.checkin_date
        LIMIT 1
    )
    WHERE EXISTS (
        SELECT 1
        FROM crm_comments
        WHERE crm_comments.crm_emp_code = checkins.emp_code
        AND crm_comments.crm_comp_code = checkins.comp_code
        AND crm_comments.comment_date = checkins.checkin_date
    )
''')
linked_count = cursor.rowcount
print(f"✅ Linked {linked_count} check-ins to comments")

conn.commit()

print("\nStep 5: Verification...")
# Verify rep types
cursor.execute('SELECT rep_type, COUNT(*) FROM reps GROUP BY rep_type ORDER BY rep_type')
print("\nRep Types Distribution:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} reps")

# Verify check-in links
cursor.execute('SELECT COUNT(*) FROM checkins WHERE comment_id IS NOT NULL')
linked = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM checkins')
total = cursor.fetchone()[0]
print(f"\nCheck-in Links:")
print(f"  Linked to comments: {linked}")
print(f"  Not linked: {total - linked}")
print(f"  Total check-ins: {total}")

conn.close()
print("\n✅ All done!")
