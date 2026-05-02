"""
Verify conversation counts in database
"""
import sqlite3

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

# Total conversations
cursor.execute('SELECT COUNT(*) FROM conversations')
total = cursor.fetchone()[0]
print(f'Total conversations: {total}')

# Check-in conversations
cursor.execute('SELECT COUNT(*) FROM conversations WHERE crm_ref LIKE "checkin_%"')
checkin_convs = cursor.fetchone()[0]
print(f'Check-in conversations: {checkin_convs}')

# Comment-based conversations
cursor.execute('SELECT COUNT(*) FROM conversations WHERE crm_ref NOT LIKE "checkin_%" OR crm_ref IS NULL')
comment_convs = cursor.fetchone()[0]
print(f'Comment-based conversations: {comment_convs}')

# By rep type
print('\nConversations by rep type:')
cursor.execute('''
    SELECT r.rep_type, COUNT(c.id) 
    FROM conversations c 
    JOIN reps r ON c.rep_id = r.id 
    GROUP BY r.rep_type
''')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Check-in conversations by rep type
print('\nCheck-in conversations by rep type:')
cursor.execute('''
    SELECT r.rep_type, COUNT(c.id) 
    FROM conversations c 
    JOIN reps r ON c.rep_id = r.id 
    WHERE c.crm_ref LIKE "checkin_%"
    GROUP BY r.rep_type
''')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Comment-based conversations by rep type
print('\nComment-based conversations by rep type:')
cursor.execute('''
    SELECT r.rep_type, COUNT(c.id) 
    FROM conversations c 
    JOIN reps r ON c.rep_id = r.id 
    WHERE c.crm_ref NOT LIKE "checkin_%" OR c.crm_ref IS NULL
    GROUP BY r.rep_type
''')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Pipeline stages
print('\nConversations by pipeline stage:')
cursor.execute('''
    SELECT pipeline_stage, COUNT(*) 
    FROM conversations 
    GROUP BY pipeline_stage 
    ORDER BY COUNT(*) DESC
''')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
