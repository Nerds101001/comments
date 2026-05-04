"""Check the actual last sync time from database."""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

# Check last sync time
cursor.execute('SELECT key, value, updated_at FROM app_settings WHERE key="last_crm_sync"')
result = cursor.fetchone()

if result:
    key, value, updated_at = result
    print(f"Last CRM Sync Setting:")
    print(f"  Key: {key}")
    print(f"  Value (ISO): {value}")
    print(f"  Updated At: {updated_at}")
    
    # Parse and show human-readable
    try:
        sync_time = datetime.fromisoformat(value)
        now = datetime.utcnow()
        diff = now - sync_time
        hours_ago = diff.total_seconds() / 3600
        print(f"\n  Parsed Time: {sync_time}")
        print(f"  Current Time: {now}")
        print(f"  Time Ago: {hours_ago:.1f} hours ago")
    except:
        print(f"  Could not parse time")
else:
    print("No last_crm_sync setting found in database")

# Check total comments
cursor.execute('SELECT COUNT(*) FROM crm_comments')
total = cursor.fetchone()[0]
print(f"\nTotal CRM Comments: {total}")

# Check pending comments
cursor.execute('SELECT COUNT(*) FROM crm_comments WHERE resolution_status="pending"')
pending = cursor.fetchone()[0]
print(f"Pending Comments: {pending}")

# Check processed comments
cursor.execute('SELECT COUNT(*) FROM crm_comments WHERE resolution_status!="pending"')
processed = cursor.fetchone()[0]
print(f"Processed Comments: {processed}")

conn.close()
