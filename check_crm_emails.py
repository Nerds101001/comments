#!/usr/bin/env python3
"""
Check what email data is available in CRM
"""
import asyncio
from app.services.crm_client import _get

async def check_emails():
    print("Checking CRM email data...")
    
    employees = await _get("/api/Employee/GetEmployeeList")
    if isinstance(employees, dict):
        employees = employees.get('Data') or employees.get('data') or []
    
    print(f"\nTotal employees: {len(employees)}")
    
    with_email = []
    without_email = []
    
    for emp in employees:
        email = emp.get('EMAIL_ADD') or emp.get('email') or emp.get('Email')
        emp_code = emp.get('EMP_CODE')
        name = emp.get('EMP_NAME')
        
        if email and str(email).strip() and str(email) != 'None' and '@' in str(email):
            with_email.append((name, emp_code, email))
        else:
            without_email.append((name, emp_code, email))
    
    print(f"\nEmployees WITH valid email: {len(with_email)}")
    print(f"Employees WITHOUT email: {len(without_email)}")
    
    print("\n=== SAMPLE WITH EMAIL ===")
    for name, code, email in with_email[:20]:
        print(f"{name:<35} | EMP: {code:<8} | Email: {email}")
    
    print(f"\n... and {len(with_email) - 20} more with emails" if len(with_email) > 20 else "")
    
    print("\n=== SAMPLE WITHOUT EMAIL ===")
    for name, code, email in without_email[:10]:
        print(f"{name:<35} | EMP: {code:<8} | Email: {email}")

if __name__ == "__main__":
    asyncio.run(check_emails())
