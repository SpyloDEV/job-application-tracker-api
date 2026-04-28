from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.reminder import Reminder
from app.repositories.reminders import ReminderRepository


class ReminderService:
    def __init__(self, session: AsyncSession) -> None:
        self.reminders = ReminderRepository(session)

    async def list_due(
        self,
        *,
        user_id: str,
        due_before: date | None = None,
    ) -> list[Reminder]:
        return await self.reminders.list_due(user_id=user_id, due_before=due_before)

    async def complete_reminder(self, *, reminder_id: str, user_id: str) -> Reminder:
        reminder = await self.reminders.get_for_user(
            reminder_id=reminder_id, user_id=user_id
        )
        if reminder is None:
            raise NotFoundError("Reminder not found.")
        return await self.reminders.complete(reminder)
