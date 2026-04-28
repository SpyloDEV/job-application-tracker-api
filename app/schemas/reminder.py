from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ReminderRead(BaseModel):
    id: str
    application_id: str
    user_id: str
    due_date: date
    title: str
    is_completed: bool
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
