
import asyncio
import os
import sys
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.abspath("."))
load_dotenv()

from app.database import get_db, engine, AsyncSessionLocal
from app.models import Rep
from app.services import crm_client

async def sync_reps():
    print("Fetching employees from CRM...")
    data = await crm_client._get("/api/Employee/GetEmployeeList")
    employees = data.get("Data") or []
    print(f"Found {len(employees)} employees.")

    async with AsyncSessionLocal() as db:
        for emp in employees:
            code = str(emp.get("EMP_CODE") or "")
            if not code: continue
            
            name = emp.get("EMP_NAME") or f"Rep {code}"
            phone = emp.get("CONTACT_NO") or ""
            avatar = emp.get("PICTURE") or ""
            
            # Check if exists
            result = await db.execute(select(Rep).where(Rep.emp_code == code))
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.name = name
                existing.phone = phone
                existing.avatar = avatar
            else:
                new_rep = Rep(
                    id=f"r_{code}",
                    emp_code=code,
                    name=name,
                    phone=phone,
                    avatar=avatar,
                    role="rep",
                    is_active=True
                )
                db.add(new_rep)
        
        await db.commit()
        print("Successfully synced reps to database.")

if __name__ == "__main__":
    asyncio.run(sync_reps())
