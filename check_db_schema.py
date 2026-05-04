import sqlite3

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(crm_comments)")
columns = cursor.fetchall()

print("CRM Comments table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
