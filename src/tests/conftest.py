"""Pytest configuration and shared fixtures."""

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from main import app
from tests.test_db import (
    TestAsyncSessionLocal,
    close_test_db,
    create_test_tables,
    drop_test_tables,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    await create_test_tables()

    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    await drop_test_tables()


@pytest_asyncio.fixture(scope="function")
async def test_app(db_session: AsyncSession) -> AsyncGenerator[FastAPI, None]:
    """Create FastAPI app with test database dependency override."""
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sync_client(test_app: FastAPI) -> TestClient:
    """Create synchronous test client for simple tests."""
    return TestClient(test_app)


@pytest_asyncio.fixture(scope="function")
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create asynchronous test client for async tests."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_test_db() -> AsyncGenerator[None, None]:
    """Clean up test database after all tests."""
    yield
    await close_test_db()


@pytest.fixture(scope="function")
def sample_wallet_data() -> dict:
    """Provide sample wallet data for testing."""
    return {
        "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "email": "test@example.com",
        "label": "Test Wallet",
    }


@pytest.fixture(scope="function")
def sample_wallet_data_telegram() -> dict:
    """Provide sample wallet data with Telegram for testing."""
    return {
        "address": "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
        "telegram_id": "123456789",
        "label": "Telegram Wallet",
    }
