from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient


async def test_due_reminders_can_be_completed(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_application: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    await create_application(company_name="Reminder Co", follow_up_date="2026-04-28")

    due_response = await client.get("/api/v1/reminders/due", headers=auth_headers)
    assert due_response.status_code == 200
    reminders = due_response.json()
    assert len(reminders) == 1
    assert reminders[0]["title"] == "Follow up with Reminder Co"

    complete_response = await client.patch(
        f"/api/v1/reminders/{reminders[0]['id']}/complete",
        headers=auth_headers,
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["is_completed"] is True

    due_after_completion = await client.get(
        "/api/v1/reminders/due", headers=auth_headers
    )
    assert due_after_completion.json() == []


async def test_user_cannot_complete_another_users_reminder(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_application: Callable[..., Awaitable[dict[str, Any]]],
    register_user: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    await create_application(follow_up_date="2026-04-28")
    due_response = await client.get("/api/v1/reminders/due", headers=auth_headers)
    reminder_id = due_response.json()[0]["id"]
    outsider = await register_user(email="reminder-outsider@example.com")

    response = await client.patch(
        f"/api/v1/reminders/{reminder_id}/complete",
        headers={"Authorization": f"Bearer {outsider['access_token']}"},
    )
    assert response.status_code == 404
