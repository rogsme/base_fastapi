from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class HealthService:
    """Service for health check operations."""

    @staticmethod
    async def check_health(db: AsyncSession) -> Dict[str, Any]:
        """Check API health status including database connectivity.

        Args:
            db: Database session dependency

        Returns:
            Dictionary containing health status information
        """
        health_status: Dict[str, Any] = {
            "status": "healthy",
            "service": "satsbell-api",
            "checks": {
                "database": "unknown",
            },
        }

        # Check database connectivity
        try:
            result = await db.execute(text("SELECT 1"))
            if result.scalar() == 1:
                health_status["checks"]["database"] = "healthy"
            else:
                health_status["checks"]["database"] = "unhealthy"
                health_status["status"] = "unhealthy"
        except Exception:
            health_status["checks"]["database"] = "unhealthy"
            health_status["status"] = "unhealthy"

        return health_status
