"""Tests for HealthService."""

from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.healthcheck import HealthService


@pytest.fixture
def mock_db_session() -> Generator[AsyncMock, None, None]:
    """Create a mock database session for health check tests."""
    with patch("services.healthcheck.AsyncSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        yield mock_session


class TestHealthService:
    """Test cases for HealthService."""

    @pytest.mark.asyncio
    async def test_check_health_success(self, db_session: AsyncSession) -> None:
        """Test successful health check."""
        result = await HealthService.check_health(db_session)

        assert result["status"] == "healthy"
        assert result["service"] == "satsbell-api"
        assert "checks" in result
        assert "database" in result["checks"]
        assert result["checks"]["database"] == "healthy"

    @pytest.mark.asyncio
    async def test_check_health_database_failure(
        self,
        mock_db_session: AsyncMock,
    ) -> None:
        """Test health check when database fails."""
        mock_db_session.execute = AsyncMock(
            side_effect=Exception("DB connection failed"),
        )

        result = await HealthService.check_health(mock_db_session)

        assert result["status"] == "unhealthy"
        assert result["service"] == "satsbell-api"
        assert result["checks"]["database"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_check_health_database_wrong_result(
        self,
        mock_db_session: AsyncMock,
    ) -> None:
        """Test health check when database returns unexpected result."""
        mock_result = AsyncMock()
        mock_result.scalar.return_value = 2  # Should be 1
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await HealthService.check_health(mock_db_session)

        assert result["status"] == "unhealthy"
        assert result["checks"]["database"] == "unhealthy"
