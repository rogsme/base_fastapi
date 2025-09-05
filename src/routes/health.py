from fastapi import APIRouter

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
async def health_check() -> dict:
    """Check API health status.

    Returns:
        Dictionary containing health status information
    """
    return await HealthService.check_health()
