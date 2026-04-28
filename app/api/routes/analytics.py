from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.analytics import AnalyticsBucket, AnalyticsOverview
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def overview(current_user: CurrentUser, session: DbSession) -> AnalyticsOverview:
    return await AnalyticsService(session).overview(user_id=current_user.id)


@router.get("/by-status", response_model=list[AnalyticsBucket])
async def by_status(
    current_user: CurrentUser, session: DbSession
) -> list[AnalyticsBucket]:
    return await AnalyticsService(session).by_status(user_id=current_user.id)


@router.get("/by-source", response_model=list[AnalyticsBucket])
async def by_source(
    current_user: CurrentUser, session: DbSession
) -> list[AnalyticsBucket]:
    return await AnalyticsService(session).by_source(user_id=current_user.id)
