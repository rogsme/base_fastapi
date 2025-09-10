from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from services.healthcheck import HealthService

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get(
    "",
    response_model=dict,
    summary="Health Check",
    description="Check if the API is running and healthy.",
    responses={
        200: {"description": "API is healthy"},
    },
)
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Check API health status.

    Args:
        db: Database session dependency

    Returns:
        Dictionary containing health status information
    """
    return await HealthService.check_health(db)
