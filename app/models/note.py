from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ApplicationNote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "application_notes"

    application_id: Mapped[str] = mapped_column(
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    content: Mapped[str] = mapped_column(Text)

    application = relationship("JobApplication", back_populates="application_notes")
    author = relationship("User", back_populates="notes")
