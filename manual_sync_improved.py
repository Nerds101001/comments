"""
Improved Manual CRM Sync and Process Script

This script:
1. Shows detailed status before sync
2. Allows you to specify hours_back for sync
3. Shows what was synced
4. Processes pending comments with progress
5. Shows detailed results

Usage:
    python manual_sync_improved.py              # Sync last 1 hour
    python manual_sync_improved.py --hours 24   # Sync last 24 hours
    python manual_sync_improved.py --hours 720  # Sync last 30 days
"""
import asyncio
import httpx
import argparse
from datetime import datetime

API_BASE = "http://localhost:8002"


async def main(hours_back: int = None):
    print("=" * 70)
    print("Improved Manual CRM Sync and Process")
    print("=" * 70)
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
            print(f"  Total Comments: {status.get('total_count', 0):,}")
            print(f"  Processed: {status.get('processed_count', 0):,}")
            print(f"  Pending: {status.get('pending_count', 0):,}")
            print()
            
            pending_before = status.get('pending_count', 0)
            
            if pending_before == 0:
                print("  ⚠️  No pending comments found!")
                print("  This means either:")
                print("     - All comments are already processed")
                print("     - No comments have been synced yet")
                print()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return
        
        # Step 2: Check a few pending comments
        if pending_before > 0:
            print("Step 2: Sample Pending Comments (first 3):")
            try:
                resp = await client.get(f"{API_BASE}/api/crm/comments?status=pending&limit=3")
                resp.raise_for_status()
                comments = resp.json()
                
                for i, c in enumerate(comments, 1):
                    print(f"  {i}. ID={c.get('id')} | Rep={c.get('rep_id')}")
                    print(f"     Text: {c.get('raw_text', '')[:70]}...")
                print()
            except Exception as e:
                print(f"  ❌ Error: {e}")
                print()
        
        # Step 3: Trigger sync
        sync_url = f"{API_BASE}/api/crm/sync"
        if hours_back:
            sync_url += f"?hours_back={hours_back}"
            print(f"Step 3: Triggering CRM sync (last {hours_back} hours)...")
        else:
            print("Step 3: Triggering CRM sync (incremental)...")
        
        try:
            resp = await client.post(sync_url)
            resp.raise_for_status()
            data = resp.json()
            
            new_comments = data.get("data", {}).get("new_comments", 0)
            hours_synced = data.get("data", {}).get("hours_back", "unknown")
            
            print(f"  ✅ Synced {new_comments} new comments (from last {hours_synced} hours)")
            
            if new_comments == 0:
                print("  ℹ️  No new comments found in CRM")
                print("  This could mean:")
                print("     - No new comments in the time window")
                print("     - All comments already in database")
                print("     - CRM API not returning data")
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()
        
        # Step 4: Check status after sync
        print("Step 4: Status after sync...")
        try:
            resp = await client.get(f"{API_BASE}/api/crm/sync-status")
            resp.raise_for_status()
            data = resp.json()
            status = data.get("data", {})
            
            pending_after_sync = status.get('pending_count', 0)
            print(f"  Pending now: {pending_after_sync:,}")
            
            if pending_after_sync == 0:
                print("  ⚠️  Still no pending comments!")
                print("  Skipping processing step.")
                print()
                return
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return
        
        # Step 5: Process pending comments in batches
        print("Step 5: Processing pending comments...")
        print("  (Processes 50 comments per batch)")
        print()
        
        batch = 1
        total_processed = 0
        total_errors = 0
        
        while True:
            print(f"  Batch {batch}: Processing up to 50 comments...")
            try:
                resp = await client.post(f"{API_BASE}/api/crm/process-all")
                resp.raise_for_status()
                data = resp.json()
                
                processed = data.get("data", {}).get("processed", 0)
                errors = data.get("data", {}).get("errors", 0)
                
                if processed == 0 and errors == 0:
                    print(f"    ⚠️  No comments processed (0 processed, 0 errors)")
                    print(f"    This means no pending comments were found.")
                    break
                
                print(f"    ✅ Processed: {processed}, Errors: {errors}")
                
                total_processed += processed
                total_errors += errors
                
                # If we processed less than 50, we're done
                if processed < 50:
                    print(f"  ✅ Completed! Processed {total_processed} comments total")
                    break
                
                batch += 1
                
                # Safety limit: stop after 20 batches (1000 comments)
                if batch > 20:
                    print(f"  ⚠️  Reached batch limit (20 batches)")
                    print(f"  Processed {total_processed} comments so far.")
                    print(f"  Run script again to process more.")
                    break
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                break
        
        print()
        
        # Step 6: Final status
        print("Step 6: Final status...")
        try:
            resp = await client.get(f"{API_BASE}/api/crm/sync-status")
            resp.raise_for_status()
            data = resp.json()
            status = data.get("data", {})
            
            print(f"  Last Sync: {status.get('last_sync', 'Never')}")
            print(f"  Total Comments: {status.get('total_count', 0):,}")
            print(f"  Processed: {status.get('processed_count', 0):,}")
            print(f"  Pending: {status.get('pending_count', 0):,}")
            print()
            
            pending_final = status.get('pending_count', 0)
            cleared = pending_before - pending_final
            
            print("=" * 70)
            print(f"Summary:")
            print(f"  - Cleared {cleared:,} pending comments")
            print(f"  - Processed {total_processed:,} comments")
            print(f"  - Errors: {total_errors}")
            print("=" * 70)
        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manual CRM sync and process")
    parser.add_argument(
        "--hours",
        type=int,
        default=None,
        help="How many hours back to sync (default: incremental since last sync)"
    )
    args = parser.parse_args()
    
    asyncio.run(main(hours_back=args.hours))
