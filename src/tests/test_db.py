"""Test database configuration for pytest."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
    },
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_test_tables() -> None:
    """Create all tables in test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_test_tables() -> None:
    """Drop all tables from test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_test_db() -> None:
    """Close test database connections."""
    await test_engine.dispose()
