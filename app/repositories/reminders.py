from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder


class ReminderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_for_user(self, *, reminder_id: str, user_id: str) -> Reminder | None:
        result = await self.session.execute(
            select(Reminder).where(
                Reminder.id == reminder_id, Reminder.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_due(
        self, *, user_id: str, due_before: date | None = None
    ) -> list[Reminder]:
        cutoff = due_before or date.today()
        result = await self.session.execute(
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.is_completed.is_(False),
                Reminder.due_date <= cutoff,
            )
            .order_by(Reminder.due_date.asc())
        )
        return list(result.scalars().all())

    async def create_or_update_for_application(
        self,
        *,
        application_id: str,
        user_id: str,
        due_date: date,
        title: str,
    ) -> Reminder:
        result = await self.session.execute(
            select(Reminder).where(
                Reminder.application_id == application_id,
                Reminder.user_id == user_id,
                Reminder.is_completed.is_(False),
            )
        )
        reminder = result.scalar_one_or_none()
        if reminder is None:
            reminder = Reminder(application_id=application_id, user_id=user_id)
            self.session.add(reminder)
        reminder.due_date = due_date
        reminder.title = title
        await self.session.flush()
        return reminder

    async def complete(self, reminder: Reminder) -> Reminder:
        reminder.is_completed = True
        reminder.completed_at = datetime.now(UTC)
        await self.session.flush()
        return reminder
