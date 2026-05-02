from datetime import UTC, date, datetime, timedelta

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import (
    ApplicationSource,
    ApplicationStatus,
    JobApplication,
    RemoteType,
)


class ApplicationRepository:
    sort_columns = {
        "created_at": JobApplication.created_at,
        "applied_at": JobApplication.applied_at,
        "follow_up_date": JobApplication.follow_up_date,
        "salary": JobApplication.salary_max,
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_for_user(
        self,
        *,
        application_id: str,
        user_id: str,
    ) -> JobApplication | None:
        result = await self.session.execute(
            select(JobApplication).where(
                JobApplication.id == application_id,
                JobApplication.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        *,
        user_id: str,
        limit: int,
        offset: int,
        status: ApplicationStatus | None = None,
        source: ApplicationSource | None = None,
        remote_type: RemoteType | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[JobApplication], int]:
        filters = [JobApplication.user_id == user_id]
        if status is not None:
            filters.append(JobApplication.status == status)
        if source is not None:
            filters.append(JobApplication.source == source)
        if remote_type is not None:
            filters.append(JobApplication.remote_type == remote_type)
        if search:
            pattern = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(JobApplication.company_name).like(pattern),
                    func.lower(JobApplication.job_title).like(pattern),
                )
            )

        total = await self.session.scalar(
            select(func.count()).select_from(JobApplication).where(*filters)
        )
        sort_column = self.sort_columns.get(sort_by, JobApplication.created_at)
        if sort_order == "asc":
            order_by = sort_column.asc().nullslast()
        else:
            order_by = sort_column.desc().nullslast()
        result = await self.session.execute(
            select(JobApplication)
            .where(*filters)
            .order_by(order_by)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all()), int(total or 0)

    async def create(self, *, user_id: str, data: dict) -> JobApplication:
        application = JobApplication(user_id=user_id, **data)
        self.session.add(application)
        await self.session.flush()
        return application

    async def delete(self, application: JobApplication) -> None:
        await self.session.delete(application)
        await self.session.flush()

    async def overview(self, *, user_id: str) -> dict:
        now = datetime.now(UTC)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        in_seven_days = date.today() + timedelta(days=7)
        result = await self.session.execute(
            select(
                func.count(JobApplication.id),
                func.avg(JobApplication.salary_min),
                func.avg(JobApplication.salary_max),
                func.sum(
                    case(
                        (
                            JobApplication.follow_up_date.is_not(None)
                            & (JobApplication.follow_up_date <= in_seven_days),
                            1,
                        ),
                        else_=0,
                    )
                ),
                func.sum(case((JobApplication.created_at >= week_start, 1), else_=0)),
                func.sum(case((JobApplication.created_at >= month_start, 1), else_=0)),
            ).where(JobApplication.user_id == user_id)
        )
        row = result.one()
        return {
            "total_applications": int(row[0] or 0),
            "average_salary_min": (
                round(float(row[1]), 2) if row[1] is not None else None
            ),
            "average_salary_max": (
                round(float(row[2]), 2) if row[2] is not None else None
            ),
            "upcoming_follow_ups": int(row[3] or 0),
            "applications_created_this_week": int(row[4] or 0),
            "applications_created_this_month": int(row[5] or 0),
        }

    async def count_by_field(self, *, user_id: str, field) -> list[tuple[str, int]]:
        result = await self.session.execute(
            select(field, func.count(JobApplication.id))
            .where(JobApplication.user_id == user_id)
            .group_by(field)
            .order_by(func.count(JobApplication.id).desc())
        )
        return [(str(row[0]), int(row[1])) for row in result.all()]
