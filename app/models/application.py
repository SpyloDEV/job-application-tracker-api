from datetime import date
from enum import StrEnum

from sqlalchemy import Date, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


def enum_values(enum_cls):
    return [item.value for item in enum_cls]


class ApplicationStatus(StrEnum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW = "interview"
    TECHNICAL_TEST = "technical_test"
    OFFER = "offer"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ApplicationSource(StrEnum):
    WELLFOUND = "Wellfound"
    LINKEDIN = "LinkedIn"
    INDEED = "Indeed"
    WEWORKREMOTELY = "WeWorkRemotely"
    REMOTEOK = "RemoteOK"
    HACKERRANK = "HackerRank"
    TURING = "Turing"
    UPWORK = "Upwork"
    OTHER = "Other"


class RemoteType(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    FLEXIBLE = "flexible"


class JobApplication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_applications"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    company_name: Mapped[str] = mapped_column(String(180), index=True)
    job_title: Mapped[str] = mapped_column(String(220), index=True)
    job_url: Mapped[str | None] = mapped_column(String(1000))
    location: Mapped[str | None] = mapped_column(String(180))
    remote_type: Mapped[RemoteType] = mapped_column(
        Enum(RemoteType, values_callable=enum_values, native_enum=False),
        default=RemoteType.REMOTE,
        index=True,
        nullable=False,
    )
    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str | None] = mapped_column(String(3))
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, values_callable=enum_values, native_enum=False),
        default=ApplicationStatus.SAVED,
        index=True,
        nullable=False,
    )
    source: Mapped[ApplicationSource] = mapped_column(
        Enum(ApplicationSource, values_callable=enum_values, native_enum=False),
        default=ApplicationSource.OTHER,
        index=True,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    applied_at: Mapped[date | None] = mapped_column(Date, index=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, index=True)

    user = relationship("User", back_populates="applications")
    application_notes = relationship(
        "ApplicationNote",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    reminders = relationship(
        "Reminder",
        back_populates="application",
        cascade="all, delete-orphan",
    )
