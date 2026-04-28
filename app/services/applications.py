from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationAppError
from app.models.application import (
    ApplicationSource,
    ApplicationStatus,
    JobApplication,
    RemoteType,
)
from app.repositories.applications import ApplicationRepository
from app.repositories.reminders import ReminderRepository


class ApplicationService:
    def __init__(self, session: AsyncSession) -> None:
        self.applications = ApplicationRepository(session)
        self.reminders = ReminderRepository(session)

    async def create_application(self, *, user_id: str, data: dict) -> JobApplication:
        data = self._normalize_data(data)
        self._validate_salary(data)
        application = await self.applications.create(user_id=user_id, data=data)
        if application.follow_up_date is not None:
            await self._sync_reminder(application)
        return application

    async def list_applications(
        self,
        *,
        user_id: str,
        limit: int,
        offset: int,
        status: ApplicationStatus | None,
        source: ApplicationSource | None,
        remote_type: RemoteType | None,
        search: str | None,
        sort_by: str,
        sort_order: str,
    ) -> tuple[list[JobApplication], int]:
        return await self.applications.list_for_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
            status=status,
            source=source,
            remote_type=remote_type,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def get_application(
        self,
        *,
        application_id: str,
        user_id: str,
    ) -> JobApplication:
        application = await self.applications.get_for_user(
            application_id=application_id,
            user_id=user_id,
        )
        if application is None:
            raise NotFoundError("Application not found.")
        return application

    async def update_application(
        self,
        *,
        application_id: str,
        user_id: str,
        data: dict,
    ) -> JobApplication:
        application = await self.get_application(
            application_id=application_id,
            user_id=user_id,
        )
        data = self._normalize_data(data)
        merged = {
            "salary_min": data.get("salary_min", application.salary_min),
            "salary_max": data.get("salary_max", application.salary_max),
        }
        self._validate_salary(merged)
        for key, value in data.items():
            setattr(application, key, value)
        if "follow_up_date" in data and application.follow_up_date is not None:
            await self._sync_reminder(application)
        return application

    async def delete_application(self, *, application_id: str, user_id: str) -> None:
        application = await self.get_application(
            application_id=application_id,
            user_id=user_id,
        )
        await self.applications.delete(application)

    async def _sync_reminder(self, application: JobApplication) -> None:
        await self.reminders.create_or_update_for_application(
            application_id=application.id,
            user_id=application.user_id,
            due_date=application.follow_up_date,
            title=f"Follow up with {application.company_name}",
        )

    def _normalize_data(self, data: dict) -> dict:
        normalized = dict(data)
        if normalized.get("job_url") is not None:
            normalized["job_url"] = str(normalized["job_url"])
        if normalized.get("currency") is not None:
            normalized["currency"] = normalized["currency"].upper()
        return normalized

    def _validate_salary(self, data: dict) -> None:
        salary_min = data.get("salary_min")
        salary_max = data.get("salary_max")
        if (
            salary_min is not None
            and salary_max is not None
            and salary_min > salary_max
        ):
            raise ValidationAppError(
                "salary_min must be less than or equal to salary_max."
            )
