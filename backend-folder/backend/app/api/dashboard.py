import logging

from fastapi import APIRouter, HTTPException, status

from app.models.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

dashboard_service = DashboardService()
router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    responses={
        200: {"description": "Dashboard data retrieved successfully"},
        404: {"description": "No sensor data available"},
        500: {"description": "Dashboard retrieval failed"},
    },
)
async def get_dashboard() -> DashboardResponse:
    """Return the latest dashboard view for the vehicle."""
    try:
        dashboard_data = dashboard_service.get_latest_dashboard()
        if dashboard_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sensor data found.",
            )

        return DashboardResponse(success=True, data=dashboard_data)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to fetch dashboard data: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard data.",
        ) from exc
