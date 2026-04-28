from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient


async def test_create_list_filter_search_update_and_delete_application(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_application: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    application = await create_application()
    assert application["company_name"] == "Acme Labs"
    assert application["status"] == "applied"

    await create_application(
        company_name="Northstar AI",
        job_title="Platform Engineer",
        status="interview",
        source="LinkedIn",
        remote_type="hybrid",
        salary_min=95000,
        salary_max=135000,
    )

    list_response = await client.get(
        "/api/v1/applications?status=interview&search=platform",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    page = list_response.json()
    assert page["total"] == 1
    assert page["items"][0]["company_name"] == "Northstar AI"

    update_response = await client.patch(
        f"/api/v1/applications/{application['id']}",
        headers=auth_headers,
        json={"status": "technical_test", "salary_max": 125000},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "technical_test"

    delete_response = await client.delete(
        f"/api/v1/applications/{application['id']}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 200

    missing_response = await client.get(
        f"/api/v1/applications/{application['id']}",
        headers=auth_headers,
    )
    assert missing_response.status_code == 404


async def test_user_cannot_access_another_users_application(
    client: AsyncClient,
    create_application: Callable[..., Awaitable[dict[str, Any]]],
    register_user: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    application = await create_application()
    outsider = await register_user(email="outsider@example.com")
    outsider_headers = {"Authorization": f"Bearer {outsider['access_token']}"}

    response = await client.get(
        f"/api/v1/applications/{application['id']}",
        headers=outsider_headers,
    )
    assert response.status_code == 404

    delete_response = await client.delete(
        f"/api/v1/applications/{application['id']}",
        headers=outsider_headers,
    )
    assert delete_response.status_code == 404
