from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import JobApplication
from app.repositories.applications import ApplicationRepository
from app.schemas.analytics import AnalyticsBucket, AnalyticsOverview


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.applications = ApplicationRepository(session)

    async def overview(self, *, user_id: str) -> AnalyticsOverview:
        return AnalyticsOverview(**await self.applications.overview(user_id=user_id))

    async def by_status(self, *, user_id: str) -> list[AnalyticsBucket]:
        rows = await self.applications.count_by_field(
            user_id=user_id,
            field=JobApplication.status,
        )
        return [AnalyticsBucket(key=key, count=count) for key, count in rows]

    async def by_source(self, *, user_id: str) -> list[AnalyticsBucket]:
        rows = await self.applications.count_by_field(
            user_id=user_id,
            field=JobApplication.source,
        )
        return [AnalyticsBucket(key=key, count=count) for key, count in rows]
