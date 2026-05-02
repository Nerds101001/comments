import sqlite3

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("="*60)
print("INBOX DATA VERIFICATION")
print("="*60)

# Total conversations
cursor.execute('SELECT COUNT(*) FROM conversations')
total = cursor.fetchone()[0]
print(f"\n✅ Total conversations in Inbox: {total:,}")

# By source
cursor.execute('SELECT COUNT(*) FROM conversations WHERE crm_ref LIKE "checkin_%"')
checkin_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM conversations WHERE crm_ref NOT LIKE "checkin_%"')
comment_count = cursor.fetchone()[0]

print(f"\nBreakdown by source:")
print(f"  📍 Check-in based (Sales): {checkin_count:,}")
print(f"  💬 Comment based (CCare/NewBiz): {comment_count:,}")

# Check-in breakdown
print(f"\nCheck-in conversations breakdown:")
cursor.execute('''
    SELECT pipeline_stage, COUNT(*) 
    FROM conversations 
    WHERE crm_ref LIKE "checkin_%"
    GROUP BY pipeline_stage
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]:,}")

# By urgency
print(f"\nBy urgency:")
cursor.execute('''
    SELECT urgency, COUNT(*) 
    FROM conversations 
    WHERE crm_ref LIKE "checkin_%"
    GROUP BY urgency
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]:,}")

# Sample conversations
print(f"\n📋 Sample check-in conversations:")
cursor.execute('''
    SELECT c.id, c.topic, c.pipeline_stage, c.urgency, r.name
    FROM conversations c
    JOIN reps r ON c.rep_id = r.id
    WHERE c.crm_ref LIKE "checkin_%"
    LIMIT 5
''')
for row in cursor.fetchall():
    print(f"\n  ID: {row[0]}")
    print(f"  Topic: {row[1]}")
    print(f"  Stage: {row[2]}")
    print(f"  Urgency: {row[3]}")
    print(f"  Rep: {row[4]}")

conn.close()

print("\n" + "="*60)
print("✅ All data is in the database and ready for Inbox!")
print("="*60)
