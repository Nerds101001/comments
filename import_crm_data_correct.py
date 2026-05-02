"""
Import CRM comments with correct field mapping from CRM JSON.
This script properly maps:
- EMP_NAME -> rep name
- EMP_CODE -> employee code
- Designation -> role
- COMP_NAME -> customer name
- COMP_CODE -> customer code
"""
import json
import sqlite3
from datetime import datetime

# Load CRM comments
with open('crm_comments_full.json', 'r', encoding='utf-8') as f:
    crm_data = json.load(f)

print(f"Loaded {len(crm_data)} comments from CRM")

# Connect to database
conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

# First, clear existing data
print("\nClearing existing data...")
cursor.execute("DELETE FROM crm_comments")
cursor.execute("DELETE FROM reps WHERE id LIKE 'r_%'")  # Keep seed reps r1-r6
cursor.execute("DELETE FROM customers WHERE id NOT IN ('cu1', 'cu2', 'cu3', 'cu4', 'cu5', 'cu6', 'cu7')")  # Keep seed customers
conn.commit()

# Extract unique reps and customers from CRM data
reps_dict = {}
customers_dict = {}

for item in crm_data:
    emp_code = str(item.get('EMP_CODE', ''))
    emp_name = item.get('EMP_NAME') or 'Unknown'
    designation = item.get('Designation') or 'Sales Person'
    
    comp_code = str(item.get('COMP_CODE', ''))
    comp_name = item.get('COMP_NAME') or 'Unknown Company'
    city = item.get('CITY') or ''
    state = item.get('STATE') or ''
    
    # Store unique reps
    if emp_code and emp_code not in reps_dict:
        reps_dict[emp_code] = {
            'name': emp_name,
            'designation': designation
        }
    
    # Store unique customers
    if comp_code and comp_code not in customers_dict:
        customers_dict[comp_code] = {
            'name': comp_name,
            'city': city,
            'state': state
        }

print(f"\nFound {len(reps_dict)} unique reps")
print(f"Found {len(customers_dict)} unique customers")

# Generate avatar initials
def get_avatar(name):
    if not name:
        return "??"
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) >= 2:
        return parts[0][:2].upper()
    else:
        return "??"

# Generate colors for avatars
colors = [
    "#007AFF", "#34C759", "#FF9500", "#FF3B30", "#AF52DE",
    "#5AC8FA", "#5856D6", "#FF2D55", "#FFCC00", "#00C7BE"
]

# Insert reps
print("\nInserting reps...")
rep_count = 0
for emp_code, rep_data in reps_dict.items():
    rep_id = f"r_{emp_code}"
    avatar = get_avatar(rep_data['name'])
    color = colors[rep_count % len(colors)]
    
    cursor.execute("""
        INSERT INTO reps (id, name, emp_code, phone, region, avatar, color, intensity, language, role, reports_to_id, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rep_id,
        rep_data['name'],
        emp_code,
        '',  # No phone in CRM data
        '',  # No region in CRM data
        avatar,
        color,
        'standard',
        'hinglish_80',
        rep_data['designation'],
        None,  # No reporting structure in CRM data
        1
    ))
    rep_count += 1

print(f"Inserted {rep_count} reps")

# Insert customers
print("\nInserting customers...")
cust_count = 0
for comp_code, cust_data in customers_dict.items():
    cust_id = f"c_{comp_code}"
    
    cursor.execute("""
        INSERT INTO customers (id, comp_code, name, city, state, cust_type, last_order_days, products_bought, ltv, cross_sell, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cust_id,
        comp_code,
        cust_data['name'],
        cust_data['city'],
        cust_data['state'],
        'regular',  # Default type
        None,
        '[]',  # Empty JSON array
        'unknown',
        '[]',  # Empty JSON array
        None
    ))
    cust_count += 1

print(f"Inserted {cust_count} customers")

# Insert CRM comments
print("\nInserting CRM comments...")
comment_count = 0
skipped = 0

for item in crm_data:
    comment_text = (item.get('Comment') or '').strip()
    
    # Skip empty or very short comments
    if not comment_text or len(comment_text) < 3:
        skipped += 1
        continue
    
    emp_code = str(item.get('EMP_CODE', ''))
    comp_code = str(item.get('COMP_CODE', ''))
    comment_date = item.get('CreatedOn', '')
    
    rep_id = f"r_{emp_code}" if emp_code else None
    customer_id = f"c_{comp_code}" if comp_code else None
    
    cursor.execute("""
        INSERT INTO crm_comments (
            crm_comment_id, rep_id, customer_id, crm_emp_code, crm_comp_code,
            raw_text, comment_date, processed_summary, followup_question,
            followup_sent, followup_sent_at, rep_reply, rep_reply_at,
            confidence_score, resolution_status, conversation_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        None,  # No CRM comment ID in data
        rep_id,
        customer_id,
        emp_code,
        comp_code,
        comment_text,
        comment_date,
        None,  # Not processed yet
        None,  # No followup yet
        0,     # Not sent
        None,
        None,
        None,
        None,
        'pending',
        None,
        datetime.utcnow().isoformat()
    ))
    comment_count += 1

conn.commit()
conn.close()

print(f"\nInserted {comment_count} comments")
print(f"Skipped {skipped} empty/short comments")

print("\n" + "="*80)
print("IMPORT COMPLETE!")
print("="*80)
print(f"✅ Reps: {rep_count}")
print(f"✅ Customers: {cust_count}")
print(f"✅ Comments: {comment_count}")
print(f"⚠️  Skipped: {skipped}")
print("\nAll data imported successfully with correct field mapping!")
