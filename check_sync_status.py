import sqlite3
from datetime import datetime

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

# Check last sync
cursor.execute('SELECT key, value, updated_at FROM app_settings WHERE key = "last_crm_sync"')
result = cursor.fetchone()

if result:
    print(f"Last CRM Sync:")
    print(f"  Key: {result[0]}")
    print(f"  Value: {result[1]}")
    print(f"  Updated: {result[2]}")
    
    # Parse and show time difference
    try:
        last_sync = datetime.fromisoformat(result[1])
        now = datetime.utcnow()
        diff = now - last_sync
        hours = diff.total_seconds() / 3600
        print(f"  Time since last sync: {hours:.1f} hours ago")
    except:
        print("  Could not parse date")
else:
    print("No last_crm_sync record found")

# Check pending comments
cursor.execute('SELECT COUNT(*) FROM crm_comments WHERE resolution_status = "pending"')
pending = cursor.fetchone()[0]
print(f"\nPending comments: {pending}")

# Check total comments
cursor.execute('SELECT COUNT(*) FROM crm_comments')
total = cursor.fetchone()[0]
print(f"Total comments: {total}")

# Check processed comments
cursor.execute('SELECT COUNT(*) FROM crm_comments WHERE resolution_status != "pending"')
processed = cursor.fetchone()[0]
print(f"Processed comments: {processed}")

conn.close()
