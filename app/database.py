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
    """Create all tables and seed default data if needed."""
    from app.models import (  # noqa: F401 — ensure models are imported
        Rep, Senior, Customer, Conversation, Message, SeniorMessage,
        StyleSample, StyleProfile, CRMComment, AppSetting
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
