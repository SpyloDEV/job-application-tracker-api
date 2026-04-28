from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.reminder import ReminderRead
from app.services.reminders import ReminderService

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.get("/due", response_model=list[ReminderRead])
async def due_reminders(
    current_user: CurrentUser,
    session: DbSession,
    due_before: date | None = Query(default=None),
) -> list[ReminderRead]:
    return await ReminderService(session).list_due(
        user_id=current_user.id,
        due_before=due_before,
    )


@router.patch("/{reminder_id}/complete", response_model=ReminderRead)
async def complete_reminder(
    reminder_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> ReminderRead:
    reminder = await ReminderService(session).complete_reminder(
        reminder_id=reminder_id,
        user_id=current_user.id,
    )
    await session.commit()
    await session.refresh(reminder)
    return reminder
