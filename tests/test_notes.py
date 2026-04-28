from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient


async def test_notes_lifecycle(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_application: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    application = await create_application()

    create_response = await client.post(
        f"/api/v1/applications/{application['id']}/notes",
        headers=auth_headers,
        json={"content": "Recruiter call scheduled for Friday."},
    )
    assert create_response.status_code == 201
    note = create_response.json()

    list_response = await client.get(
        f"/api/v1/applications/{application['id']}/notes",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = await client.patch(
        f"/api/v1/notes/{note['id']}",
        headers=auth_headers,
        json={"content": "Recruiter call moved to Monday."},
    )
    assert update_response.status_code == 200
    assert update_response.json()["content"].endswith("Monday.")

    delete_response = await client.delete(
        f"/api/v1/notes/{note['id']}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 200


async def test_user_cannot_add_note_to_another_users_application(
    client: AsyncClient,
    create_application: Callable[..., Awaitable[dict[str, Any]]],
    register_user: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    application = await create_application()
    outsider = await register_user(email="notes-outsider@example.com")

    response = await client.post(
        f"/api/v1/applications/{application['id']}/notes",
        headers={"Authorization": f"Bearer {outsider['access_token']}"},
        json={"content": "This should not be accepted."},
    )
    assert response.status_code == 404
