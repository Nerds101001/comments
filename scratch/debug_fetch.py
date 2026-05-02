
import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.abspath("."))
load_dotenv()

from app.services import crm_client

async def debug_fetch():
    print("--- CRM DEBUG FETCH ---")
    try:
        # 1. Fetch Employee List
        print("Fetching Employee List...")
        data = await crm_client._get("/api/Employee/GetEmployeeList")
        print(f"Full response type: {type(data)}")
        if isinstance(data, dict):
            for k, v in data.items():
                print(f"Key: {k}, Type: {type(v)}, Value: {v if not isinstance(v, (list, dict)) else '...'}")
                if isinstance(v, list):
                    print(f"  - List length: {len(v)}")
                    if v: print(f"  - First item: {v[0]}")
        else:
            print(f"Raw data: {data}")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_fetch())
