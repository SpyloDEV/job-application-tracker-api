from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient


async def test_analytics_overview_status_and_source_breakdowns(
    client: AsyncClient,
    auth_headers: dict[str, str],
    create_application: Callable[..., Awaitable[dict[str, Any]]],
) -> None:
    await create_application(
        company_name="Acme Labs",
        status="applied",
        source="Wellfound",
        salary_min=80000,
        salary_max=110000,
    )
    await create_application(
        company_name="SignalWorks",
        status="interview",
        source="LinkedIn",
        salary_min=90000,
        salary_max=130000,
    )
    await create_application(
        company_name="BuildOps",
        status="applied",
        source="LinkedIn",
        salary_min=100000,
        salary_max=140000,
    )

    overview_response = await client.get(
        "/api/v1/analytics/overview", headers=auth_headers
    )
    assert overview_response.status_code == 200
    overview = overview_response.json()
    assert overview["total_applications"] == 3
    assert overview["average_salary_min"] == 90000
    assert overview["average_salary_max"] == 126666.67
    assert overview["upcoming_follow_ups"] == 3

    status_response = await client.get(
        "/api/v1/analytics/by-status", headers=auth_headers
    )
    status_counts = {item["key"]: item["count"] for item in status_response.json()}
    assert status_counts == {"applied": 2, "interview": 1}

    source_response = await client.get(
        "/api/v1/analytics/by-source", headers=auth_headers
    )
    source_counts = {item["key"]: item["count"] for item in source_response.json()}
    assert source_counts == {"LinkedIn": 2, "Wellfound": 1}
