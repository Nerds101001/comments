"""
Create conversations from check-ins for sales reps
"""
import sqlite3
import uuid
from datetime import datetime

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("Creating conversations from check-ins for sales reps...")
print("="*60)

# Get all check-ins that don't have a linked comment (need follow-up)
cursor.execute('''
    SELECT c.id, c.emp_code, c.emp_name, c.comp_code, c.comp_name, 
           c.checkin_date, c.checkin_time, c.address, c.comment_id
    FROM checkins c
    WHERE c.comment_id IS NULL
    AND c.comp_code IS NOT NULL 
    AND c.comp_code != '0'
    AND c.comp_code != ''
''')
checkins_without_comments = cursor.fetchall()

print(f"Found {len(checkins_without_comments)} check-ins without comments")

# Get rep_id mapping (emp_code -> rep_id)
cursor.execute('SELECT emp_code, id, rep_type FROM reps')
rep_mapping = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

# Get customer_id mapping (comp_code -> customer_id)
cursor.execute('SELECT comp_code, id FROM customers')
customer_mapping = {row[0]: row[1] for row in cursor.fetchall()}

created = 0
skipped = 0
sales_only = 0

for checkin_id, emp_code, emp_name, comp_code, comp_name, checkin_date, checkin_time, address, comment_id in checkins_without_comments:
    # Get rep info
    if emp_code not in rep_mapping:
        skipped += 1
        continue
    
    rep_id, rep_type = rep_mapping[emp_code]
    
    # Only create conversations for sales reps
    if rep_type != 'sales':
        skipped += 1
        continue
    
    sales_only += 1
    
    # Get customer_id
    customer_id = customer_mapping.get(comp_code)
    
    # Check if conversation already exists for this check-in
    cursor.execute('''
        SELECT id FROM conversations 
        WHERE crm_ref = ?
    ''', (f"checkin_{checkin_id}",))
    
    if cursor.fetchone():
        skipped += 1
        continue
    
    # Create conversation
    conv_id = f"conv_{uuid.uuid4().hex[:12]}"
    topic = f"Visit to {comp_name or 'Customer'} - {checkin_date}"
    
    # Create conversation
    cursor.execute('''
        INSERT INTO conversations (
            id, rep_id, customer_id, topic, pipeline_stage, objective, tactic,
            urgency, handler, handler_reason, ai_confidence, is_fresh,
            crm_ref, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        conv_id,
        rep_id,
        customer_id,
        topic,
        "visit_followup",
        f"Get details about visit to {comp_name or 'customer'}",
        "Ask about visit details and outcomes",
        "medium",
        "ai",
        "Check-in without comment - needs follow-up",
        70,
        True,
        f"checkin_{checkin_id}",
        datetime.utcnow(),
        datetime.utcnow()
    ))
    
    # Create initial message from AI asking about the visit
    cursor.execute('''
        INSERT INTO messages (
            conversation_id, from_who, text, ts, date_label, 
            status, is_read, by_ai, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        conv_id,
        'mukul',
        f"Hi {emp_name.split()[0]}, I see you visited {comp_name or 'a customer'} on {checkin_date} at {checkin_time}. What was discussed during this visit?",
        checkin_time or "09:00",
        "today",
        "sent",
        False,
        True,
        datetime.utcnow()
    ))
    
    created += 1
    
    if created % 100 == 0:
        print(f"  Created {created} conversations...")

conn.commit()

print(f"\n✅ Done!")
print(f"   Total check-ins without comments: {len(checkins_without_comments)}")
print(f"   Sales rep check-ins: {sales_only}")
print(f"   Conversations created: {created}")
print(f"   Skipped: {skipped}")

# Verification
cursor.execute('''
    SELECT COUNT(*) FROM conversations 
    WHERE crm_ref LIKE 'checkin_%'
''')
total_checkin_convs = cursor.fetchone()[0]

print(f"\nTotal conversations from check-ins: {total_checkin_convs}")

# Show some examples
print("\nExample conversations:")
cursor.execute('''
    SELECT c.id, c.topic, c.rep_id, r.name, c.urgency
    FROM conversations c
    JOIN reps r ON c.rep_id = r.id
    WHERE c.crm_ref LIKE 'checkin_%'
    LIMIT 5
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} (Rep: {row[3]}, Urgency: {row[4]})")

conn.close()
