"""
Reorganize conversations to be customer-centric instead of comment-centric.
One conversation per Rep-Customer pair, with all comments as messages.
"""
import sqlite3
from datetime import datetime
import uuid

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("Reorganizing conversations to customer-centric model...")
print("="*60)

# Step 1: Backup current conversations
cursor.execute('SELECT COUNT(*) FROM conversations')
old_count = cursor.fetchone()[0]
print(f"Current conversations: {old_count}")

# Step 2: Clear existing conversations and messages
print("\nClearing old conversation structure...")
cursor.execute('DELETE FROM messages')
cursor.execute('DELETE FROM conversations')
conn.commit()
print("✅ Cleared old data")

# Step 3: Get all CRM comments grouped by rep and customer
print("\nGrouping comments by Rep-Customer pairs...")
cursor.execute('''
    SELECT 
        cc.rep_id,
        cc.customer_id,
        cc.crm_comp_code,
        r.name as rep_name,
        r.rep_type,
        c.name as customer_name,
        COUNT(*) as comment_count
    FROM crm_comments cc
    LEFT JOIN reps r ON cc.rep_id = r.id
    LEFT JOIN customers c ON cc.customer_id = c.id
    WHERE cc.rep_id IS NOT NULL
    GROUP BY cc.rep_id, cc.customer_id
    ORDER BY comment_count DESC
''')
rep_customer_pairs = cursor.fetchall()

print(f"Found {len(rep_customer_pairs)} unique Rep-Customer pairs")

# Step 4: Create one conversation per Rep-Customer pair
created_convs = 0
created_msgs = 0

for rep_id, customer_id, comp_code, rep_name, rep_type, customer_name, comment_count in rep_customer_pairs:
    # Create conversation
    conv_id = f"conv_{uuid.uuid4().hex[:12]}"
    
    # Determine topic based on rep type
    if rep_type == 'sales':
        topic = f"Sales: {customer_name or comp_code}"
        pipeline_stage = "Sales follow-up"
    elif rep_type == 'ccare':
        topic = f"Customer Care: {customer_name or comp_code}"
        pipeline_stage = "Customer support"
    elif rep_type == 'newbiz':
        topic = f"New Business: {customer_name or comp_code}"
        pipeline_stage = "New business development"
    else:
        topic = f"{customer_name or comp_code}"
        pipeline_stage = "Follow-up"
    
    objective = f"Manage relationship with {customer_name or comp_code}"
    tactic = f"Review {comment_count} interactions and provide guidance"
    
    cursor.execute('''
        INSERT INTO conversations (
            id, rep_id, customer_id, topic, pipeline_stage, objective, tactic,
            intel, urgency, handler, ai_confidence, is_fresh,
            is_resolved, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        conv_id,
        rep_id,
        customer_id,
        topic,
        pipeline_stage,
        objective,
        tactic,
        f"{comment_count} interactions recorded",
        "medium",
        "ai",
        75,
        True,
        False,
        datetime.utcnow(),
        datetime.utcnow()
    ))
    
    # Get all comments for this rep-customer pair
    cursor.execute('''
        SELECT id, raw_text, comment_date, created_at
        FROM crm_comments
        WHERE rep_id = ? AND customer_id = ?
        ORDER BY created_at ASC
    ''', (rep_id, customer_id))
    
    comments = cursor.fetchall()
    
    # Add each comment as a message
    for comment_id, raw_text, comment_date, created_at in comments:
        # Parse comment to make it readable
        if raw_text.startswith('[CRM Visit Note]'):
            # It's already formatted
            text = raw_text
        else:
            # Format it nicely
            text = f"[CRM Comment - {comment_date or 'Recent'}]\n{raw_text}"
        
        # Parse created_at if it's a string
        if isinstance(created_at, str):
            try:
                created_at_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                ts = created_at_dt.strftime("%H:%M")
            except:
                ts = "09:00"
                created_at_dt = datetime.utcnow()
        elif created_at:
            ts = created_at.strftime("%H:%M")
            created_at_dt = created_at
        else:
            ts = "09:00"
            created_at_dt = datetime.utcnow()
        
        cursor.execute('''
            INSERT INTO messages (
                conversation_id, from_who, text, ts, date_label,
                status, is_read, by_ai, by_mukul_real, requires_approval, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            conv_id,
            'rep',
            text,
            ts,
            "today",
            "received",
            False,
            False,
            False,
            False,
            created_at_dt
        ))
        
        created_msgs += 1
        
        # Link comment to conversation
        cursor.execute('''
            UPDATE crm_comments 
            SET conversation_id = ?
            WHERE id = ?
        ''', (conv_id, comment_id))
    
    created_convs += 1
    
    if created_convs % 100 == 0:
        conn.commit()
        print(f"  Created {created_convs} conversations with {created_msgs} messages...")

# Step 5: Handle check-ins
print("\nAdding check-in data to conversations...")
cursor.execute('''
    SELECT 
        c.id, c.emp_code, c.comp_code, c.checkin_date, c.checkin_time,
        c.address, c.comment_id, r.id as rep_id, cu.id as customer_id
    FROM checkins c
    LEFT JOIN reps r ON c.emp_code = r.emp_code
    LEFT JOIN customers cu ON c.comp_code = cu.comp_code
    WHERE r.id IS NOT NULL AND cu.id IS NOT NULL
    ORDER BY c.checkin_date DESC, c.checkin_time DESC
''')
checkins = cursor.fetchall()

checkin_msgs = 0
for checkin_id, emp_code, comp_code, checkin_date, checkin_time, address, comment_id, rep_id, customer_id in checkins:
    # Find or create conversation for this rep-customer pair
    cursor.execute('''
        SELECT id FROM conversations
        WHERE rep_id = ? AND customer_id = ?
        LIMIT 1
    ''', (rep_id, customer_id))
    
    result = cursor.fetchone()
    if result:
        conv_id = result[0]
    else:
        # Create new conversation
        conv_id = f"conv_{uuid.uuid4().hex[:12]}"
        cursor.execute('''
            SELECT name FROM customers WHERE id = ?
        ''', (customer_id,))
        cust_name = cursor.fetchone()[0]
        
        cursor.execute('''
            INSERT INTO conversations (
                id, rep_id, customer_id, topic, pipeline_stage, objective, tactic,
                urgency, handler, ai_confidence, is_fresh, is_resolved, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            conv_id, rep_id, customer_id,
            f"Sales: {cust_name}",
            "Sales follow-up",
            f"Manage relationship with {cust_name}",
            "Review visits and provide guidance",
            "medium", "ai", 75, True, False,
            datetime.utcnow(), datetime.utcnow()
        ))
        created_convs += 1
    
    # Add check-in as a message
    text = f"🚗 [Visit - {checkin_date}]\n"
    text += f"Time: {checkin_time}\n"
    if address:
        text += f"Location: {address}\n"
    
    if comment_id:
        # Get the comment
        cursor.execute('SELECT raw_text FROM crm_comments WHERE id = ?', (comment_id,))
        comment_row = cursor.fetchone()
        if comment_row:
            text += f"\nComment: {comment_row[0]}"
    else:
        text += "\n⚠️ No comment added for this visit"
    
    cursor.execute('''
        INSERT INTO messages (
            conversation_id, from_who, text, ts, date_label,
            status, is_read, by_ai, by_mukul_real, requires_approval, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        conv_id, 'rep', text,
        checkin_time or "09:00", "today",
        "received", False, False, False, False,
        datetime.utcnow()
    ))
    
    checkin_msgs += 1

conn.commit()

print(f"\n✅ Reorganization complete!")
print(f"\nResults:")
print(f"  Old conversations: {old_count}")
print(f"  New conversations: {created_convs}")
print(f"  Comment messages: {created_msgs}")
print(f"  Check-in messages: {checkin_msgs}")
print(f"  Total messages: {created_msgs + checkin_msgs}")
print(f"\nReduction: {old_count} → {created_convs} conversations")
print(f"Average messages per conversation: {(created_msgs + checkin_msgs) / created_convs:.1f}")

# Show some examples
print("\n" + "="*60)
print("Example conversations:")
cursor.execute('''
    SELECT c.id, c.topic, r.name, cu.name, COUNT(m.id) as msg_count
    FROM conversations c
    JOIN reps r ON c.rep_id = r.id
    LEFT JOIN customers cu ON c.customer_id = cu.id
    LEFT JOIN messages m ON m.conversation_id = c.id
    GROUP BY c.id
    ORDER BY msg_count DESC
    LIMIT 5
''')
for row in cursor.fetchall():
    print(f"\n{row[1]}")
    print(f"  Rep: {row[2]}")
    print(f"  Customer: {row[3]}")
    print(f"  Messages: {row[4]}")

conn.close()
print("\n" + "="*60)
