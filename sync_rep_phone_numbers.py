#!/usr/bin/env python3
"""
Sync rep phone numbers and emails from CRM Employee API
"""
import asyncio
import sqlite3
from app.services.crm_client import _get

async def sync_rep_contact_data():
    print("=" * 100)
    print("SYNCING REP CONTACT DATA FROM CRM")
    print("=" * 100)
    
    # Fetch employee list from CRM
    print("\n1. Fetching employee list from CRM API...")
    try:
        employees = await _get("/api/Employee/GetEmployeeList")
        
        # Handle different response formats
        if isinstance(employees, dict):
            employees = employees.get('Data') or employees.get('data') or employees.get('Result') or []
        
        print(f"   ✅ Fetched {len(employees)} employees from CRM")
        
        # Show sample of what we got
        if employees and len(employees) > 0:
            print("\n2. Sample employee data:")
            sample = employees[0]
            print(f"   Keys available: {list(sample.keys())}")
            print(f"   Sample: {sample}")
        
    except Exception as e:
        print(f"   ❌ Failed to fetch employees: {e}")
        return
    
    # Connect to database
    print("\n3. Updating database...")
    conn = sqlite3.connect('hitech_sales.db')
    cursor = conn.cursor()
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for emp in employees:
        try:
            # Extract employee data (handle different field name cases)
            emp_code = (emp.get('EMP_CODE') or emp.get('emp_code') or 
                       emp.get('EmpCode') or emp.get('empCode') or 
                       emp.get('EmployeeCode') or emp.get('employeeCode'))
            
            phone = (emp.get('CONTACT_NO') or emp.get('MOBILE') or emp.get('mobile') or 
                    emp.get('Mobile') or emp.get('MobileNo') or 
                    emp.get('mobileNo') or emp.get('Phone') or 
                    emp.get('phone') or emp.get('PHONE'))
            
            email = (emp.get('EMAIL_ADD') or emp.get('EMAIL') or emp.get('email') or 
                    emp.get('Email') or emp.get('EmailId') or 
                    emp.get('emailId'))
            
            # Clean and validate email
            if email and str(email).strip() and str(email) != 'None' and '@' in str(email):
                email = str(email).strip()
            else:
                email = None
            
            name = (emp.get('EMP_NAME') or emp.get('emp_name') or 
                   emp.get('Name') or emp.get('name') or 
                   emp.get('EmployeeName') or emp.get('employeeName'))
            
            if not emp_code:
                skipped_count += 1
                continue
            
            # Check if rep exists in our database
            cursor.execute("SELECT id, name FROM reps WHERE emp_code = ?", (str(emp_code),))
            rep = cursor.fetchone()
            
            if not rep:
                skipped_count += 1
                continue
            
            # Update phone number and email if available
            updates = []
            params = []
            
            if phone and str(phone).strip() and str(phone) != 'None':
                updates.append("phone = ?")
                params.append(str(phone).strip())
            
            if email and str(email).strip() and str(email) != 'None':
                updates.append("email = ?")
                params.append(str(email).strip())
            
            if updates:
                params.append(str(emp_code))
                cursor.execute(f"""
                    UPDATE reps 
                    SET {', '.join(updates)}
                    WHERE emp_code = ?
                """, params)
                updated_count += 1
                
                phone_display = phone if phone else 'N/A'
                email_display = email if email else 'N/A'
                print(f"   ✅ Updated {rep[1]:<35} | EMP: {emp_code:<8} | Phone: {phone_display:<20} | Email: {email_display}")
            else:
                print(f"   ⚠️  No contact data for {rep[1]:<35} | EMP: {emp_code:<8}")
                skipped_count += 1
            
        except Exception as e:
            print(f"   ❌ Error processing employee {emp_code}: {e}")
            error_count += 1
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 100)
    print("SYNC COMPLETE")
    print("=" * 100)
    print(f"✅ Updated: {updated_count} reps")
    print(f"⚠️  Skipped: {skipped_count} reps (no phone or not in database)")
    print(f"❌ Errors:  {error_count} reps")
    print("=" * 100)
    
    # Run verification
    print("\n" + "=" * 100)
    print("VERIFICATION")
    print("=" * 100)
    
    conn = sqlite3.connect('hitech_sales.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN phone IS NOT NULL AND phone != '' AND phone != 'NULL' THEN 1 END) as with_phone,
            COUNT(CASE WHEN email IS NOT NULL AND email != '' AND email != 'NULL' THEN 1 END) as with_email,
            COUNT(CASE WHEN phone IS NOT NULL AND phone != '' AND phone != 'NULL' 
                       AND email IS NOT NULL AND email != '' AND email != 'NULL' THEN 1 END) as with_both
        FROM reps
        WHERE is_active = 1
    """)
    
    stats = cursor.fetchone()
    print(f"Active reps in database:     {stats[0]}")
    print(f"Active reps with phone:      {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
    print(f"Active reps with email:      {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")
    print(f"Active reps with BOTH:       {stats[3]} ({stats[3]/stats[0]*100:.1f}%)")
    print(f"Active reps still missing:   {stats[0] - stats[3]} ({(stats[0]-stats[3])/stats[0]*100:.1f}%)")
    
    if stats[3] == stats[0]:
        print("\n✅ SUCCESS! All active reps now have phone numbers AND email addresses!")
        print("   Ready to send AI nudges via WhatsApp and Email!")
    elif stats[3] > stats[0] * 0.8:
        print(f"\n⚠️  {stats[3]} reps have both phone and email ({stats[3]/stats[0]*100:.1f}%)")
        print(f"   {stats[0] - stats[3]} reps still need complete contact info")
        print("   Check if these reps exist in CRM with both phone and email")
    else:
        print(f"\n❌ Only {stats[3]} reps have both phone and email ({stats[3]/stats[0]*100:.1f}%)")
        print("   Most reps are still missing contact information")
        print("   Check CRM API response format or employee data")
    
    conn.close()
    print("=" * 100)

if __name__ == "__main__":
    asyncio.run(sync_rep_contact_data())
