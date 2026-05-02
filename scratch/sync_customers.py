
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
from app.models import Customer
from app.services import crm_client

async def sync_customers():
    print("Fetching customers from CRM...")
    # Fetching without empCode to get all (if admin)
    customers = await crm_client.get_customer_list()
    print(f"Found {len(customers)} customers.")

    async with AsyncSessionLocal() as db:
        for cust in customers:
            comp_code = str(cust.get("compCode") or cust.get("CompCode") or "")
            if not comp_code: continue
            
            name = cust.get("compName") or cust.get("CompName") or f"Customer {comp_code}"
            city = cust.get("city") or cust.get("City") or ""
            state = cust.get("state") or cust.get("State") or ""
            phone = cust.get("contactNo") or cust.get("ContactNo") or ""
            
            # Check if exists
            result = await db.execute(select(Customer).where(Customer.comp_code == comp_code))
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.name = name
                existing.city = city
                existing.state = state
                existing.phone = phone
            else:
                new_cust = Customer(
                    id=f"c_{comp_code}",
                    comp_code=comp_code,
                    name=name,
                    city=city,
                    state=state,
                    phone=phone,
                    cust_type="regular"
                )
                db.add(new_cust)
        
        await db.commit()
        print("Successfully synced customers to database.")

if __name__ == "__main__":
    asyncio.run(sync_customers())
