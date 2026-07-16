from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import AnalyticsOverviewResponse, ModelUsageItem
from app.services.analytics_service import get_model_usage, get_overview_metrics

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def analytics_overview(
    project_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    metrics = get_overview_metrics(db, project_id=project_id)
    return AnalyticsOverviewResponse(**metrics)


@router.get("/models", response_model=list[ModelUsageItem])
async def analytics_models(
    project_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    rows = get_model_usage(db, project_id=project_id)
    return [ModelUsageItem(**row) for row in rows]
