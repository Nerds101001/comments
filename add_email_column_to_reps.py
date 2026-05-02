#!/usr/bin/env python3
"""
Add email column to reps table and sync emails from CRM
"""
import sqlite3

def add_email_column():
    conn = sqlite3.connect('hitech_sales.db')
    cursor = conn.cursor()
    
    print("=" * 100)
    print("ADDING EMAIL COLUMN TO REPS TABLE")
    print("=" * 100)
    
    # Check if email column already exists
    cursor.execute("PRAGMA table_info(reps)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'email' in columns:
        print("\n✅ Email column already exists in reps table")
    else:
        print("\n1. Adding email column to reps table...")
        try:
            cursor.execute("ALTER TABLE reps ADD COLUMN email VARCHAR(100)")
            conn.commit()
            print("   ✅ Email column added successfully")
        except Exception as e:
            print(f"   ❌ Failed to add email column: {e}")
            conn.close()
            return
    
    # Verify the column was added
    cursor.execute("PRAGMA table_info(reps)")
    columns = cursor.fetchall()
    
    print("\n2. Current reps table schema:")
    for col in columns:
        print(f"   - {col[1]:<20} {col[2]:<15}")
    
    conn.close()
    print("\n" + "=" * 100)
    print("✅ SCHEMA UPDATE COMPLETE")
    print("=" * 100)
    print("\nNext step: Run sync_rep_phone_numbers.py to populate email addresses")
    print("=" * 100)

if __name__ == "__main__":
    add_email_column()
