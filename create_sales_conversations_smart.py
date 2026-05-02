"""
Create conversations for sales reps using BOTH check-ins and comments
"""
import sqlite3
import uuid
from datetime import datetime

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("Creating smart conversations for sales reps...")
print("="*60)

# Get rep_id mapping (emp_code -> rep_id)
cursor.execute('SELECT emp_code, id, name, rep_type FROM reps')
rep_mapping = {row[0]: (row[1], row[2], row[3]) for row in cursor.fetchall()}

# Get customer_id mapping (comp_code -> customer_id)
cursor.execute('SELECT comp_code, id, name FROM customers')
customer_mapping = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

# Get all check-ins for sales reps
cursor.execute('''
    SELECT c.id, c.emp_code, c.emp_name, c.comp_code, c.comp_name, 
           c.checkin_date, c.checkin_time, c.address, c.comment_id
    FROM checkins c
    WHERE c.comp_code IS NOT NULL 
    AND c.comp_code != '0'
    AND c.comp_code != ''
    ORDER BY c.checkin_date DESC, c.checkin_time DESC
''')
all_checkins = cursor.fetchall()

print(f"Found {len(all_checkins)} total check-ins")

created_with_comment = 0
created_without_comment = 0
skipped = 0
non_sales = 0

for checkin_id, emp_code, emp_name, comp_code, comp_name, checkin_date, checkin_time, address, comment_id in all_checkins:
    # Get rep info
    if emp_code not in rep_mapping:
        skipped += 1
        continue
    
    rep_id, rep_name, rep_type = rep_mapping[emp_code]
    
    # Only process sales reps
    if rep_type != 'sales':
        non_sales += 1
        continue
    
    # Get customer_id
    customer_id, customer_name = customer_mapping.get(comp_code, (None, comp_name))
    
    # Check if conversation already exists for this check-in
    cursor.execute('''
        SELECT id FROM conversations 
        WHERE crm_ref = ?
    ''', (f"checkin_{checkin_id}",))
    
    if cursor.fetchone():
        skipped += 1
        continue
    
    # Create conversation ID
    conv_id = f"conv_{uuid.uuid4().hex[:12]}"
    
    # CASE 1: Check-in HAS a comment
    if comment_id:
        # Get the comment
        cursor.execute('''
            SELECT id, raw_text, comment_date, processed_summary
            FROM crm_comments
            WHERE id = ?
        ''', (comment_id,))
        comment_row = cursor.fetchone()
        
        if comment_row:
            comment_text = comment_row[1]
            
            # Create conversation with comment context
            topic = f"Visit: {customer_name or comp_name} - {checkin_date}"
            objective = f"Follow up on visit to {customer_name or comp_name}"
            tactic = "Review visit details and plan next steps"
            
            cursor.execute('''
                INSERT INTO conversations (
                    id, rep_id, customer_id, topic, pipeline_stage, objective, tactic,
                    intel, urgency, handler, handler_reason, ai_confidence, is_fresh,
                    is_resolved, crm_ref, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                conv_id,
                rep_id,
                customer_id,
                topic,
                "visit_completed",
                objective,
                tactic,
                f"Visit on {checkin_date} at {checkin_time}. Location: {address or 'N/A'}. Comment: {comment_text}",
                "medium",
                "ai",
                "Visit with comment - ready for AI nudge",
                85,
                True,
                False,
                f"checkin_{checkin_id}",
                datetime.utcnow(),
                datetime.utcnow()
            ))
            
            # Create initial message showing the visit info
            cursor.execute('''
                INSERT INTO messages (
                    conversation_id, from_who, text, ts, date_label, 
                    status, is_read, by_ai, by_mukul_real, requires_approval, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                conv_id,
                'mukul',
                f"Visit Summary:\n📍 {customer_name or comp_name}\n📅 {checkin_date} at {checkin_time}\n💬 {comment_text}\n\nGreat work! I'll generate a follow-up nudge for you.",
                checkin_time or "09:00",
                "today",
                "sent",
                False,
                True,
                False,
                False,
                datetime.utcnow()
            ))
            
            created_with_comment += 1
    
    # CASE 2: Check-in WITHOUT comment (needs follow-up)
    else:
        topic = f"Visit: {customer_name or comp_name} - {checkin_date} (No Comment)"
        objective = f"Get details about visit to {customer_name or comp_name}"
        tactic = "Ask rep what happened during the visit"
        
        cursor.execute('''
            INSERT INTO conversations (
                id, rep_id, customer_id, topic, pipeline_stage, objective, tactic,
                intel, urgency, handler, handler_reason, ai_confidence, is_fresh,
                is_resolved, crm_ref, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            conv_id,
            rep_id,
            customer_id,
            topic,
            "visit_pending_comment",
            objective,
            tactic,
            f"Visit on {checkin_date} at {checkin_time}. Location: {address or 'N/A'}. No comment added yet.",
            "high",  # Higher urgency for missing comments
            "ai",
            "Check-in without comment - needs immediate follow-up",
            60,
            True,
            False,
            f"checkin_{checkin_id}",
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        # Create message asking about the visit
        first_name = rep_name.split()[0] if rep_name else "there"
        cursor.execute('''
            INSERT INTO messages (
                conversation_id, from_who, text, ts, date_label, 
                status, is_read, by_ai, by_mukul_real, requires_approval, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            conv_id,
            'mukul',
            f"Hi {first_name}, I noticed you visited {customer_name or comp_name} on {checkin_date} at {checkin_time}, but no comment was added. Could you share what was discussed during this visit?",
            checkin_time or "09:00",
            "today",
            "sent",
            False,
            True,
            False,
            False,
            datetime.utcnow()
        ))
        
        created_without_comment += 1
    
    if (created_with_comment + created_without_comment) % 100 == 0:
        print(f"  Processed {created_with_comment + created_without_comment} conversations...")

conn.commit()

print(f"\n✅ Done!")
print(f"   Total check-ins: {len(all_checkins)}")
print(f"   Non-sales reps: {non_sales}")
print(f"   Conversations with comment: {created_with_comment}")
print(f"   Conversations without comment: {created_without_comment}")
print(f"   Skipped (already exist): {skipped}")
print(f"   Total created: {created_with_comment + created_without_comment}")

# Verification
cursor.execute('''
    SELECT COUNT(*) FROM conversations 
    WHERE crm_ref LIKE 'checkin_%'
''')
total_checkin_convs = cursor.fetchone()[0]

print(f"\nTotal conversations from check-ins in DB: {total_checkin_convs}")

# Show breakdown by pipeline stage
print("\nConversations by stage:")
cursor.execute('''
    SELECT pipeline_stage, COUNT(*) 
    FROM conversations 
    WHERE crm_ref LIKE 'checkin_%'
    GROUP BY pipeline_stage
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Show some examples
print("\nExample conversations WITH comments:")
cursor.execute('''
    SELECT c.id, c.topic, r.name, c.urgency, c.ai_confidence
    FROM conversations c
    JOIN reps r ON c.rep_id = r.id
    WHERE c.crm_ref LIKE 'checkin_%'
    AND c.pipeline_stage = 'visit_completed'
    LIMIT 3
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")
    print(f"    Rep: {row[2]}, Urgency: {row[3]}, Confidence: {row[4]}%")

print("\nExample conversations WITHOUT comments:")
cursor.execute('''
    SELECT c.id, c.topic, r.name, c.urgency
    FROM conversations c
    JOIN reps r ON c.rep_id = r.id
    WHERE c.crm_ref LIKE 'checkin_%'
    AND c.pipeline_stage = 'visit_pending_comment'
    LIMIT 3
''')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")
    print(f"    Rep: {row[2]}, Urgency: {row[3]}")

conn.close()
