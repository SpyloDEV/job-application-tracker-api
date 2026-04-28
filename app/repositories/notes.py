from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import ApplicationNote


class NoteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_for_user(
        self, *, note_id: str, user_id: str
    ) -> ApplicationNote | None:
        result = await self.session.execute(
            select(ApplicationNote).where(
                ApplicationNote.id == note_id,
                ApplicationNote.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_application(
        self,
        *,
        application_id: str,
        user_id: str,
    ) -> list[ApplicationNote]:
        result = await self.session.execute(
            select(ApplicationNote)
            .where(
                ApplicationNote.application_id == application_id,
                ApplicationNote.user_id == user_id,
            )
            .order_by(ApplicationNote.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        application_id: str,
        user_id: str,
        content: str,
    ) -> ApplicationNote:
        note = ApplicationNote(
            application_id=application_id,
            user_id=user_id,
            content=content,
        )
        self.session.add(note)
        await self.session.flush()
        return note

    async def delete(self, note: ApplicationNote) -> None:
        await self.session.delete(note)
        await self.session.flush()
