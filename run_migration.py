"""
One-shot migration script — run this on Railway via:
  python run_migration.py

Or via Railway CLI:
  railway run python run_migration.py
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncConnection


def _normalise_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def run():
    raw_url = os.environ.get("DATABASE_URL", "")
    if not raw_url:
        print("❌ DATABASE_URL not set")
        return

    db_url = _normalise_url(raw_url)
    is_sqlite = "sqlite" in db_url
    print(f"🔌 Connecting to: {db_url[:40]}...")

    engine = create_async_engine(db_url)

    async with engine.begin() as conn:
        if is_sqlite:
            await run_sqlite(conn)
        else:
            await run_postgres(conn)

    await engine.dispose()
    print("\n✅ Migration complete!")


async def run_postgres(conn: AsyncConnection):
    print("🐘 PostgreSQL — running migrations...\n")

    steps = [
        ("reps.email",                "ALTER TABLE reps ADD COLUMN IF NOT EXISTS email VARCHAR(200)"),
        ("reps.rep_type",             "ALTER TABLE reps ADD COLUMN IF NOT EXISTS rep_type VARCHAR(20) DEFAULT 'sales'"),
        ("checkins.crm_id",           "ALTER TABLE checkins ADD COLUMN IF NOT EXISTS crm_id INTEGER"),
        ("crm_comments.followup_sent_at", "ALTER TABLE crm_comments ADD COLUMN IF NOT EXISTS followup_sent_at TIMESTAMP"),
        ("crm_comments.rep_reply_at", "ALTER TABLE crm_comments ADD COLUMN IF NOT EXISTS rep_reply_at TIMESTAMP"),
        ("ix_checkins_crm_id index",  "CREATE UNIQUE INDEX IF NOT EXISTS ix_checkins_crm_id ON checkins(crm_id) WHERE crm_id IS NOT NULL"),
    ]

    for label, sql in steps:
        try:
            await conn.execute(text(sql))
            print(f"  ✅ {label}")
        except Exception as e:
            print(f"  ⚠️  {label} — {e}")

    # Verify
    print("\n📋 Verifying reps columns:")
    result = await conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='reps' ORDER BY ordinal_position"
    ))
    cols = [r[0] for r in result.fetchall()]
    print(f"  Columns: {', '.join(cols)}")

    for required in ["email", "rep_type"]:
        status = "✅" if required in cols else "❌ MISSING"
        print(f"  {required}: {status}")


async def run_sqlite(conn: AsyncConnection):
    print("🗄️  SQLite — running migrations...\n")

    def _migrate(sync_conn):
        from sqlalchemy import inspect as sa_inspect
        inspector = sa_inspect(sync_conn)

        def add_col(table, col, col_type):
            existing = {c["name"] for c in inspector.get_columns(table)}
            if col not in existing:
                sync_conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                print(f"  ✅ Added {col} to {table}")
            else:
                print(f"  ✓  {col} already in {table}")

        add_col("reps", "email", "TEXT")
        add_col("reps", "rep_type", "TEXT DEFAULT 'sales'")
        add_col("checkins", "crm_id", "INTEGER")
        add_col("crm_comments", "followup_sent_at", "TIMESTAMP")
        add_col("crm_comments", "rep_reply_at", "TIMESTAMP")

    await conn.run_sync(_migrate)


if __name__ == "__main__":
    asyncio.run(run())
