from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Reminder(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reminders"

    application_id: Mapped[str] = mapped_column(
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    due_date: Mapped[date] = mapped_column(Date, index=True)
    title: Mapped[str] = mapped_column(String(220))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    application = relationship("JobApplication", back_populates="reminders")
    user = relationship("User", back_populates="reminders")
