import sqlite3

conn = sqlite3.connect('hitech_sales.db')
cursor = conn.cursor()

# Get distinct roles
cursor.execute('SELECT DISTINCT role FROM reps ORDER BY role')
roles = cursor.fetchall()
print('Current Rep Roles:')
for r in roles:
    print(f'  - {r[0]}')

# Count by type
cursor.execute('SELECT COUNT(*) FROM reps WHERE role LIKE "%Sales%"')
print(f'\nSales reps: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM reps WHERE role LIKE "%Customer Care%" OR role LIKE "%CCare%"')
print(f'CCare reps: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM reps WHERE role LIKE "%New%" OR role LIKE "%Business%"')
print(f'NewBiz reps: {cursor.fetchone()[0]}')

# Sample reps
print('\nSample reps:')
cursor.execute('SELECT emp_code, name, role FROM reps LIMIT 10')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]} - {row[2]}')

conn.close()
