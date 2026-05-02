import sqlite3

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM conversations')
conv_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM crm_comments WHERE resolution_status="pending"')
pending_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM crm_comments')
total_comments = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM messages')
message_count = cursor.fetchone()[0]

print(f"Conversations: {conv_count}")
print(f"Messages: {message_count}")
print(f"Total CRM Comments: {total_comments}")
print(f"Pending CRM Comments: {pending_count}")

conn.close()
