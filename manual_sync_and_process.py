"""
Manual CRM Sync and Process Script

This script:
1. Triggers a CRM sync to fetch new comments
2. Processes all pending comments in batches
3. Shows progress and results

Use this to:
- Test the sync and processing pipeline
- Clear the backlog of 128,189 pending comments
- Verify AI processing is working
"""
import asyncio
import httpx
from datetime import datetime

API_BASE = "http://localhost:8002"

async def main():
    print("=" * 60)
    print("Manual CRM Sync and Process")
    print("=" * 60)
    print()
    
    async with httpx.AsyncClient(timeout=300) as client:
        # Step 1: Check current status
        print("Step 1: Checking current status...")
        try:
            resp = await client.get(f"{API_BASE}/api/crm/sync-status")
            resp.raise_for_status()
            data = resp.json()
            status = data.get("data", {})
            
            print(f"  Last Sync: {status.get('last_sync', 'Never')}")
            print(f"  Total Comments: {status.get('total_count', 0)}")
            print(f"  Processed: {status.get('processed_count', 0)}")
            print(f"  Pending: {status.get('pending_count', 0)}")
            print()
            
            pending_before = status.get('pending_count', 0)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return
        
        # Step 2: Trigger sync
        print("Step 2: Triggering CRM sync...")
        try:
            resp = await client.post(f"{API_BASE}/api/crm/sync")
            resp.raise_for_status()
            data = resp.json()
            
            new_comments = data.get("data", {}).get("new_comments", 0)
            print(f"  ✅ Synced {new_comments} new comments")
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
        
        # Step 3: Process pending comments in batches
        print("Step 3: Processing pending comments...")
        print("  (This processes 50 comments at a time)")
        print()
        
        batch = 1
        total_processed = 0
        
        while True:
            print(f"  Batch {batch}: Processing up to 50 comments...")
            try:
                resp = await client.post(f"{API_BASE}/api/crm/process-all")
                resp.raise_for_status()
                data = resp.json()
                
                processed = data.get("data", {}).get("processed", 0)
                errors = data.get("data", {}).get("errors", 0)
                
                print(f"    ✅ Processed: {processed}, Errors: {errors}")
                
                total_processed += processed
                
                # If we processed less than 50, we're done
                if processed < 50:
                    print(f"  Completed! Processed {total_processed} comments total")
                    break
                
                batch += 1
                
                # Safety limit: stop after 10 batches (500 comments)
                if batch > 10:
                    print(f"  Reached batch limit. Processed {total_processed} comments.")
                    print(f"  Run script again to process more.")
                    break
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                break
        
        print()
        
        # Step 4: Check final status
        print("Step 4: Checking final status...")
        try:
            resp = await client.get(f"{API_BASE}/api/crm/sync-status")
            resp.raise_for_status()
            data = resp.json()
            status = data.get("data", {})
            
            print(f"  Last Sync: {status.get('last_sync', 'Never')}")
            print(f"  Total Comments: {status.get('total_count', 0)}")
            print(f"  Processed: {status.get('processed_count', 0)}")
            print(f"  Pending: {status.get('pending_count', 0)}")
            print()
            
            pending_after = status.get('pending_count', 0)
            cleared = pending_before - pending_after
            
            print("=" * 60)
            print(f"Summary: Cleared {cleared} pending comments")
            print("=" * 60)
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
