from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    applications = relationship(
        "JobApplication",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    notes = relationship("ApplicationNote", back_populates="author")
    reminders = relationship(
        "Reminder", back_populates="user", cascade="all, delete-orphan"
    )
