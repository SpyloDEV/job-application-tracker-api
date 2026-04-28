from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.note import ApplicationNote
from app.repositories.applications import ApplicationRepository
from app.repositories.notes import NoteRepository


class NoteService:
    def __init__(self, session: AsyncSession) -> None:
        self.applications = ApplicationRepository(session)
        self.notes = NoteRepository(session)

    async def add_note(
        self,
        *,
        application_id: str,
        user_id: str,
        content: str,
    ) -> ApplicationNote:
        application = await self.applications.get_for_user(
            application_id=application_id,
            user_id=user_id,
        )
        if application is None:
            raise NotFoundError("Application not found.")
        return await self.notes.create(
            application_id=application_id,
            user_id=user_id,
            content=content,
        )

    async def list_notes(
        self,
        *,
        application_id: str,
        user_id: str,
    ) -> list[ApplicationNote]:
        application = await self.applications.get_for_user(
            application_id=application_id,
            user_id=user_id,
        )
        if application is None:
            raise NotFoundError("Application not found.")
        return await self.notes.list_for_application(
            application_id=application_id,
            user_id=user_id,
        )

    async def update_note(
        self,
        *,
        note_id: str,
        user_id: str,
        content: str,
    ) -> ApplicationNote:
        note = await self.notes.get_for_user(note_id=note_id, user_id=user_id)
        if note is None:
            raise NotFoundError("Note not found.")
        note.content = content
        return note

    async def delete_note(self, *, note_id: str, user_id: str) -> None:
        note = await self.notes.get_for_user(note_id=note_id, user_id=user_id)
        if note is None:
            raise NotFoundError("Note not found.")
        await self.notes.delete(note)
