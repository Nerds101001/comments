"""
Export database data to SQL file for Railway deployment
"""
import asyncio
import sqlite3
from pathlib import Path

async def export_database():
    print("=" * 80)
    print("EXPORTING DATABASE FOR RAILWAY")
    print("=" * 80)
    
    db_path = Path("hitech_sales.db")
    
    if not db_path.exists():
        print(f"\n❌ Database not found: {db_path}")
        print("Make sure you're running this from the project root directory.")
        return
    
    print(f"\n✅ Found database: {db_path}")
    print(f"   Size: {db_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get table counts
    tables = ['reps', 'customers', 'conversations', 'messages', 'crm_comments', 'checkins']
    
    print("\n📊 Current Data:")
    print("─" * 80)
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table:<20} {count:>10} records")
        except:
            print(f"   {table:<20} {'N/A':>10}")
    
    # Export to SQL dump
    print("\n📦 Exporting to SQL file...")
    print("─" * 80)
    
    output_file = "railway_database_dump.sql"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("-- Hi-Tech AI Sales Database Dump\n")
        f.write("-- Generated for Railway deployment\n")
        f.write("-- Contains all reps, customers, conversations, and data\n\n")
        
        # Get schema and data
        for line in conn.iterdump():
            # Skip seed data tables (we want real data)
            if 'sqlite_sequence' in line:
                continue
            f.write(f"{line}\n")
    
    conn.close()
    
    file_size = Path(output_file).stat().st_size / 1024 / 1024
    print(f"✅ Exported to: {output_file}")
    print(f"   Size: {file_size:.2f} MB")
    
    print("\n" + "=" * 80)
    print("EXPORT COMPLETE!")
    print("=" * 80)
    
    print("\n📋 Next Steps:")
    print("─" * 80)
    print("1. Copy the database file to Railway:")
    print("   - Option A: Use Railway CLI (recommended)")
    print("   - Option B: Push database to GitHub and sync")
    print()
    print("2. See RAILWAY_DATABASE_MIGRATION.md for detailed instructions")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(export_database())
