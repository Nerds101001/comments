"""
List all employees and customers from the database
"""
import sqlite3

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

print("="*100)
print("ALL EMPLOYEES (SALES TEAM)")
print("="*100)

cursor.execute("""
    SELECT emp_code, name, role 
    FROM reps 
    WHERE id LIKE 'r_%'
    ORDER BY emp_code
""")

reps = cursor.fetchall()
print(f"\nTotal Employees: {len(reps)}\n")
print(f"{'EMP_CODE':<12} {'NAME':<35} {'DESIGNATION':<20}")
print("-"*100)

for emp_code, name, role in reps:
    print(f"{emp_code:<12} {name:<35} {role:<20}")

print("\n" + "="*100)
print("SAMPLE CUSTOMERS (First 50)")
print("="*100)

cursor.execute("""
    SELECT comp_code, name, city, state 
    FROM customers 
    WHERE id LIKE 'c_%'
    ORDER BY comp_code
    LIMIT 50
""")

customers = cursor.fetchall()

# Get total count
cursor.execute("SELECT COUNT(*) FROM customers WHERE id LIKE 'c_%'")
total_customers = cursor.fetchone()[0]

print(f"\nTotal Customers: {total_customers}")
print(f"Showing first 50:\n")
print(f"{'COMP_CODE':<12} {'COMPANY NAME':<50} {'CITY':<20} {'STATE':<20}")
print("-"*100)

for comp_code, name, city, state in customers:
    print(f"{comp_code:<12} {name:<50} {city:<20} {state:<20}")

print("\n" + "="*100)
print("COMMENTS BREAKDOWN BY DESIGNATION")
print("="*100)

cursor.execute("""
    SELECT r.role, COUNT(*) as count
    FROM crm_comments c
    JOIN reps r ON c.rep_id = r.id
    GROUP BY r.role
    ORDER BY count DESC
""")

breakdown = cursor.fetchall()
print(f"\n{'DESIGNATION':<20} {'COMMENT COUNT':<15}")
print("-"*40)

for role, count in breakdown:
    print(f"{role:<20} {count:<15}")

conn.close()

print("\n" + "="*100)
print("DATA EXPORT COMPLETE")
print("="*100)
