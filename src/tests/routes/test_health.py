"""Tests for health check endpoints."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    def test_health_check_sync(self, sync_client: TestClient) -> None:
        """Test health check endpoint with sync client."""
        response = sync_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert "service" in data
        assert "checks" in data
        assert data["service"] == "satsbell-api"

    @pytest.mark.asyncio
    async def test_health_check_async(self, async_client: AsyncClient) -> None:
        """Test health check endpoint with async client."""
        response = await async_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "status" in data
        assert "service" in data
        assert "checks" in data
        assert data["service"] == "satsbell-api"
        assert "database" in data["checks"]

    @pytest.mark.asyncio
    async def test_health_check_database_status(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that database health check works correctly."""
        response = await async_client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["checks"]["database"] == "healthy"
        assert data["status"] == "healthy"
