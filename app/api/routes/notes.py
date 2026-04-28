from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import Message
from app.schemas.note import NoteRead, NoteUpdate
from app.services.notes import NoteService

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.patch("/{note_id}", response_model=NoteRead)
async def update_note(
    note_id: str,
    payload: NoteUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> NoteRead:
    note = await NoteService(session).update_note(
        note_id=note_id,
        user_id=current_user.id,
        content=payload.content,
    )
    await session.commit()
    await session.refresh(note)
    return note


@router.delete("/{note_id}", response_model=Message)
async def delete_note(
    note_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> Message:
    await NoteService(session).delete_note(note_id=note_id, user_id=current_user.id)
    await session.commit()
    return Message(message="Note deleted.")
