import sqlite3

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("="*60)
print("CHECKING ALL CONVERSATIONS")
print("="*60)

# Total conversations
cursor.execute('SELECT COUNT(*) FROM conversations')
total = cursor.fetchone()[0]
print(f"\nTotal conversations: {total:,}")

# Check-in based
cursor.execute('SELECT COUNT(*) FROM conversations WHERE crm_ref LIKE "checkin_%"')
checkin = cursor.fetchone()[0]
print(f"Check-in based (Sales): {checkin:,}")

# Comment based (original)
cursor.execute('SELECT COUNT(*) FROM conversations WHERE crm_ref NOT LIKE "checkin_%"')
comment = cursor.fetchone()[0]
print(f"Comment based (CCare/NewBiz): {comment:,}")

# Check CRM comments
cursor.execute('SELECT COUNT(*) FROM crm_comments')
total_comments = cursor.fetchone()[0]
print(f"\nTotal CRM comments in DB: {total_comments:,}")

# Check if original conversations exist
cursor.execute('''
    SELECT COUNT(*) FROM conversations 
    WHERE crm_ref NOT LIKE "checkin_%" 
    AND crm_ref IS NOT NULL
''')
original_convs = cursor.fetchone()[0]
print(f"Original comment-based conversations: {original_convs:,}")

# Sample original conversations
print("\nSample original (comment-based) conversations:")
cursor.execute('''
    SELECT id, topic, crm_ref 
    FROM conversations 
    WHERE crm_ref NOT LIKE "checkin_%"
    AND crm_ref IS NOT NULL
    LIMIT 5
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1][:50]}... (ref: {row[2]})")

conn.close()
