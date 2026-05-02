"""
Add metadata to conversations to help with frontend filtering and display
"""
import sqlite3

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("Adding conversation metadata...")
print("="*60)

# Get all conversations with rep info
cursor.execute('''
    SELECT c.id, c.crm_ref, c.pipeline_stage, c.rep_id, r.rep_type, r.name
    FROM conversations c
    JOIN reps r ON c.rep_id = r.id
''')
conversations = cursor.fetchall()

print(f"Processing {len(conversations)} conversations...")

updated = 0
for conv_id, crm_ref, pipeline_stage, rep_id, rep_type, rep_name in conversations:
    # Determine conversation type and update topic if needed
    if crm_ref and crm_ref.startswith('checkin_'):
        # Check-in conversation
        if pipeline_stage == 'visit_pending_comment':
            # High priority - needs comment
            cursor.execute('''
                UPDATE conversations 
                SET urgency = 'high'
                WHERE id = ?
            ''', (conv_id,))
            updated += 1
        elif pipeline_stage == 'visit_completed':
            # Visit with comment
            cursor.execute('''
                UPDATE conversations 
                SET urgency = 'medium'
                WHERE id = ?
            ''', (conv_id,))
            updated += 1
    else:
        # Comment-based conversation
        # Set appropriate urgency based on rep type
        if rep_type in ['ccare', 'newbiz']:
            cursor.execute('''
                UPDATE conversations 
                SET urgency = 'medium'
                WHERE id = ? AND urgency != 'high'
            ''', (conv_id,))
            updated += 1

if updated > 0:
    conn.commit()
    print(f"✅ Updated {updated} conversations with proper urgency levels")
else:
    print("✅ All conversations already have proper metadata")

# Show summary
print("\nConversation Summary:")
print("-" * 60)

# By source and rep type
cursor.execute('''
    SELECT 
        CASE 
            WHEN c.crm_ref LIKE 'checkin_%' THEN 'Check-in'
            ELSE 'Comment'
        END as source,
        r.rep_type,
        COUNT(*) as count
    FROM conversations c
    JOIN reps r ON c.rep_id = r.id
    GROUP BY source, r.rep_type
    ORDER BY source, r.rep_type
''')
print("\nBy Source and Rep Type:")
for row in cursor.fetchall():
    print(f"  {row[0]:12} | {row[1]:8} | {row[2]:6} conversations")

# By urgency
cursor.execute('''
    SELECT urgency, COUNT(*) 
    FROM conversations 
    GROUP BY urgency
''')
print("\nBy Urgency:")
for row in cursor.fetchall():
    print(f"  {row[0]:8} | {row[1]:6} conversations")

# High priority check-ins without comments
cursor.execute('''
    SELECT COUNT(*) 
    FROM conversations 
    WHERE crm_ref LIKE 'checkin_%' 
    AND pipeline_stage = 'visit_pending_comment'
    AND urgency = 'high'
''')
high_priority = cursor.fetchone()[0]
print(f"\n⚠️  High Priority: {high_priority} visits without comments")

conn.close()
print("\n" + "="*60)
print("✅ Metadata update complete!")
