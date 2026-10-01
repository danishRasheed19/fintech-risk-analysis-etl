from fastapi import APIRouter

from src.risk_platform.analytics import get_risk_analytics


router = APIRouter(
    prefix="/api/risk",
    tags=["Risk Analytics"]
)


@router.get("/get_analytics")
def risk_analytics():
    return get_risk_analytics()