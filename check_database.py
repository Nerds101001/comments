"""Check database structure and data"""
import sqlite3
import json

# Connect to database
conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("="*80)
print("DATABASE STRUCTURE CHECK")
print("="*80)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\nTables in database: {len(tables)}")
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "="*80)
print("TABLE ROW COUNTS")
print("="*80)

# Count rows in each table
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"{table_name}: {count} rows")

print("\n" + "="*80)
print("CRM COMMENTS TABLE DETAILS")
print("="*80)

# Check if crm_comments table exists and has data
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crm_comments'")
if cursor.fetchone():
    # Get column info
    cursor.execute("PRAGMA table_info(crm_comments)")
    columns = cursor.fetchall()
    print(f"\nColumns in crm_comments table:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Get sample data
    cursor.execute("SELECT * FROM crm_comments LIMIT 5")
    rows = cursor.fetchall()
    
    print(f"\nSample data (first 5 rows):")
    if rows:
        for i, row in enumerate(rows, 1):
            print(f"\n  Row {i}:")
            for j, col in enumerate(columns):
                print(f"    {col[1]}: {row[j]}")
    else:
        print("  ⚠️ No data in crm_comments table")
else:
    print("⚠️ crm_comments table does not exist")

print("\n" + "="*80)
print("REPS TABLE")
print("="*80)

cursor.execute("SELECT id, name, emp_code, phone FROM reps")
reps = cursor.fetchall()
print(f"\nReps in database: {len(reps)}")
for rep in reps:
    print(f"  {rep[0]}: {rep[1]} (EMP {rep[2]}) - {rep[3]}")

print("\n" + "="*80)
print("CUSTOMERS TABLE")
print("="*80)

cursor.execute("SELECT COUNT(*) FROM customers")
customer_count = cursor.fetchone()[0]
print(f"\nCustomers in database: {customer_count}")

if customer_count > 0:
    cursor.execute("SELECT id, name, comp_code, city, state FROM customers LIMIT 10")
    customers = cursor.fetchall()
    print("\nSample customers:")
    for cust in customers:
        print(f"  {cust[0]}: {cust[1]} ({cust[2]}) - {cust[3]}, {cust[4]}")

print("\n" + "="*80)
print("CONVERSATIONS TABLE")
print("="*80)

cursor.execute("SELECT COUNT(*) FROM conversations")
conv_count = cursor.fetchone()[0]
print(f"\nConversations in database: {conv_count}")

if conv_count > 0:
    cursor.execute("SELECT id, topic, handler, urgency FROM conversations LIMIT 5")
    convs = cursor.fetchall()
    print("\nSample conversations:")
    for conv in convs:
        print(f"  {conv[0]}: {conv[1]} (Handler: {conv[2]}, Urgency: {conv[3]})")

conn.close()

print("\n" + "="*80)
print("DATABASE CHECK COMPLETE")
print("="*80)
