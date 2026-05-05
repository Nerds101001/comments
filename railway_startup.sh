#!/bin/bash
set -e
echo "🚀 Running Railway startup migrations..."

DB_URL="${DATABASE_URL:-}"

# ── PostgreSQL migrations (Railway production) ──────────────────────────────
if echo "$DB_URL" | grep -qE "^postgres"; then
    echo "🐘 PostgreSQL detected — running schema migrations..."

    python -c "
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Normalise URL for asyncpg driver
db_url = os.environ['DATABASE_URL']
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql+asyncpg://', 1)
elif db_url.startswith('postgresql://') and '+asyncpg' not in db_url:
    db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
# already postgresql+asyncpg:// → use as-is

engine = create_async_engine(db_url)

migrations = [
    # reps table additions
    \"\"\"ALTER TABLE reps ADD COLUMN IF NOT EXISTS email VARCHAR(200)\"\"\",
    \"\"\"ALTER TABLE reps ADD COLUMN IF NOT EXISTS rep_type VARCHAR(20) DEFAULT 'sales'\"\"\",
    # checkins table additions
    \"\"\"ALTER TABLE checkins ADD COLUMN IF NOT EXISTS crm_id INTEGER\"\"\",
    \"\"\"CREATE UNIQUE INDEX IF NOT EXISTS ix_checkins_crm_id ON checkins(crm_id) WHERE crm_id IS NOT NULL\"\"\",
    # crm_comments additions
    \"\"\"ALTER TABLE crm_comments ADD COLUMN IF NOT EXISTS followup_sent_at TIMESTAMP\"\"\",
    \"\"\"ALTER TABLE crm_comments ADD COLUMN IF NOT EXISTS rep_reply_at TIMESTAMP\"\"\",
]

async def run():
    async with engine.begin() as conn:
        for sql in migrations:
            try:
                await conn.execute(text(sql))
                print(f'  ✅ {sql[:60]}...')
            except Exception as e:
                print(f'  ⚠️  Skipped (already exists?): {e}')
    await engine.dispose()

asyncio.run(run())
"
    echo "✅ PostgreSQL migrations complete."

# ── SQLite migrations (local development) ───────────────────────────────────
else
    echo "🗄️  SQLite detected — running local migrations..."

    python -c "
import sqlite3, os
db = os.environ.get('DATABASE_URL','').replace('sqlite+aiosqlite:///','').replace('sqlite:///','') or './hitech_sales.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

def add_col(table, col, col_type):
    cur.execute(f'PRAGMA table_info({table})')
    if col not in [r[1] for r in cur.fetchall()]:
        cur.execute(f'ALTER TABLE {table} ADD COLUMN {col} {col_type}')
        print(f'  ✅ Added {col} to {table}')
    else:
        print(f'  ✓  {col} already in {table}')

add_col('reps', 'email', 'TEXT')
add_col('reps', 'rep_type', \"TEXT DEFAULT 'sales'\")
add_col('checkins', 'crm_id', 'INTEGER')
add_col('crm_comments', 'followup_sent_at', 'TIMESTAMP')
add_col('crm_comments', 'rep_reply_at', 'TIMESTAMP')

# Unique index for crm_id
try:
    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_checkins_crm_id ON checkins(crm_id) WHERE crm_id IS NOT NULL')
except Exception as e:
    print(f'  ⚠️  crm_id index: {e}')

conn.commit()
conn.close()
print('  ✅ SQLite migrations complete.')
"
fi

echo ""
echo "🚀 Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
