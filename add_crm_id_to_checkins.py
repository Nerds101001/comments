"""
Migration: add crm_id column to checkins table.
Run once: python add_crm_id_to_checkins.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "hitech_sales.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check if column already exists
cur.execute("PRAGMA table_info(checkins)")
cols = [row[1] for row in cur.fetchall()]

if "crm_id" not in cols:
    print("Adding crm_id column to checkins...")
    cur.execute("ALTER TABLE checkins ADD COLUMN crm_id INTEGER")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_checkins_crm_id ON checkins(crm_id) WHERE crm_id IS NOT NULL")
    conn.commit()
    print("✅ Done — crm_id column added and indexed.")
else:
    print("✅ crm_id column already exists — nothing to do.")

conn.close()
