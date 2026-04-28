from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.models.application import ApplicationSource, ApplicationStatus, RemoteType
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
)
from app.schemas.common import Message, Page
from app.schemas.note import NoteCreate, NoteRead
from app.services.applications import ApplicationService
from app.services.notes import NoteService

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> ApplicationRead:
    application = await ApplicationService(session).create_application(
        user_id=current_user.id,
        data=payload.model_dump(),
    )
    await session.commit()
    await session.refresh(application)
    return application


@router.get("", response_model=Page[ApplicationRead])
async def list_applications(
    current_user: CurrentUser,
    session: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    source: ApplicationSource | None = Query(default=None),
    remote_type: RemoteType | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    sort_by: str = Query(
        default="created_at", pattern="^(created_at|applied_at|follow_up_date|salary)$"
    ),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> Page[ApplicationRead]:
    applications, total = await ApplicationService(session).list_applications(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        status=status_filter,
        source=source,
        remote_type=remote_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return Page(items=applications, total=total, limit=limit, offset=offset)


@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> ApplicationRead:
    return await ApplicationService(session).get_application(
        application_id=application_id,
        user_id=current_user.id,
    )


@router.patch("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: str,
    payload: ApplicationUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> ApplicationRead:
    application = await ApplicationService(session).update_application(
        application_id=application_id,
        user_id=current_user.id,
        data=payload.model_dump(exclude_unset=True),
    )
    await session.commit()
    await session.refresh(application)
    return application


@router.delete("/{application_id}", response_model=Message)
async def delete_application(
    application_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> Message:
    await ApplicationService(session).delete_application(
        application_id=application_id,
        user_id=current_user.id,
    )
    await session.commit()
    return Message(message="Application deleted.")


@router.post(
    "/{application_id}/notes",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_note(
    application_id: str,
    payload: NoteCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> NoteRead:
    note = await NoteService(session).add_note(
        application_id=application_id,
        user_id=current_user.id,
        content=payload.content,
    )
    await session.commit()
    await session.refresh(note)
    return note


@router.get("/{application_id}/notes", response_model=list[NoteRead])
async def list_notes(
    application_id: str,
    current_user: CurrentUser,
    session: DbSession,
) -> list[NoteRead]:
    return await NoteService(session).list_notes(
        application_id=application_id,
        user_id=current_user.id,
    )
