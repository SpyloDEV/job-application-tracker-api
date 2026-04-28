from __future__ import annotations

import asyncio
import logging
from datetime import date

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.reminder import Reminder
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _load_due_reminders() -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Reminder).where(
                Reminder.is_completed.is_(False),
                Reminder.due_date <= date.today(),
            )
        )
        reminders = list(result.scalars().all())

    for reminder in reminders:
        logger.info(
            "follow_up_reminder_due",
            extra={
                "reminder_id": reminder.id,
                "application_id": reminder.application_id,
                "user_id": reminder.user_id,
                "due_date": reminder.due_date.isoformat(),
            },
        )
    return len(reminders)


@celery_app.task(name="app.workers.jobs.check_due_reminders")
def check_due_reminders() -> dict[str, int]:
    count = asyncio.run(_load_due_reminders())
    return {"due_reminders": count}
