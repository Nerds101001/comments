from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


def _get_db_url(raw: str) -> str:
    """
    Normalise the DATABASE_URL for SQLAlchemy async drivers.
    Railway provides  postgres://...  but asyncpg needs  postgresql+asyncpg://...
    aiosqlite needs   sqlite+aiosqlite://...
    """
    if raw.startswith("postgres://"):
        return raw.replace("postgres://", "postgresql+asyncpg://", 1)
    if raw.startswith("postgresql://") and "+asyncpg" not in raw:
        return raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    return raw


_db_url = _get_db_url(settings.DATABASE_URL)
_is_sqlite = "sqlite" in _db_url

engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False, "timeout": 30} if _is_sqlite else {},
    # WAL mode allows concurrent reads while one writer is active
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def _enable_wal():
    """Enable WAL mode for SQLite to allow concurrent reads during writes."""
    if _is_sqlite:
        async with engine.begin() as conn:
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA busy_timeout=30000"))


async def init_db():
    """Create all tables, then run any missing-column migrations."""
    from app.models import (  # noqa: F401 — ensure models are imported
        Rep, Senior, Customer, Conversation, Message, SeniorMessage,
        StyleSample, StyleProfile, CRMComment, AppSetting,
        AIKnowledgeBase, CheckIn
    )
    async with engine.begin() as conn:
        # Create any tables that don't exist yet
        await conn.run_sync(Base.metadata.create_all)

        # ── Column migrations (safe on every startup) ──────────────────────
        # These use IF NOT EXISTS / DO NOTHING patterns so they're idempotent.
        if _is_sqlite:
            await _sqlite_migrations(conn)
        else:
            await _postgres_migrations(conn)


async def _postgres_migrations(conn):
    """Add missing columns to existing PostgreSQL tables."""
    migrations = [
        "ALTER TABLE reps ADD COLUMN IF NOT EXISTS email VARCHAR(200)",
        "ALTER TABLE reps ADD COLUMN IF NOT EXISTS rep_type VARCHAR(20) DEFAULT 'sales'",
        "ALTER TABLE checkins ADD COLUMN IF NOT EXISTS crm_id INTEGER",
        "ALTER TABLE crm_comments ADD COLUMN IF NOT EXISTS followup_sent_at TIMESTAMP",
        "ALTER TABLE crm_comments ADD COLUMN IF NOT EXISTS rep_reply_at TIMESTAMP",
    ]
    for sql in migrations:
        try:
            await conn.execute(text(sql))
        except Exception:
            pass  # column already exists — safe to ignore

    # Unique index (CREATE INDEX IF NOT EXISTS is safe to repeat)
    try:
        await conn.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_checkins_crm_id "
            "ON checkins(crm_id) WHERE crm_id IS NOT NULL"
        ))
    except Exception:
        pass


async def _sqlite_migrations(conn):
    """Add missing columns to existing SQLite tables."""
    from sqlalchemy import inspect as sa_inspect

    def _add_if_missing(sync_conn):
        inspector = sa_inspect(sync_conn)
        existing = {c["name"] for c in inspector.get_columns("reps")}
        if "email" not in existing:
            sync_conn.execute(text("ALTER TABLE reps ADD COLUMN email TEXT"))
        if "rep_type" not in existing:
            sync_conn.execute(text("ALTER TABLE reps ADD COLUMN rep_type TEXT DEFAULT 'sales'"))

        ci_cols = {c["name"] for c in inspector.get_columns("checkins")}
        if "crm_id" not in ci_cols:
            sync_conn.execute(text("ALTER TABLE checkins ADD COLUMN crm_id INTEGER"))

        cc_cols = {c["name"] for c in inspector.get_columns("crm_comments")}
        if "followup_sent_at" not in cc_cols:
            sync_conn.execute(text("ALTER TABLE crm_comments ADD COLUMN followup_sent_at TIMESTAMP"))
        if "rep_reply_at" not in cc_cols:
            sync_conn.execute(text("ALTER TABLE crm_comments ADD COLUMN rep_reply_at TIMESTAMP"))

    await conn.run_sync(_add_if_missing)
