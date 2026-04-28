import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_job_tracker.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-job-tracker")
os.environ.setdefault("ENABLE_BACKGROUND_JOBS", "false")

from app.api import deps  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.main import app  # noqa: E402


def _engine_options(database_url: str) -> dict[str, Any]:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"poolclass": NullPool}


test_engine = create_async_engine(
    os.environ["DATABASE_URL"],
    **_engine_options(os.environ["DATABASE_URL"]),
)
TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def reset_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[deps.get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def register_user(
    client: AsyncClient,
) -> Callable[..., Awaitable[dict[str, Any]]]:
    async def _register_user(
        email: str = "dev@example.com",
        password: str = "SecurePass123!",
        full_name: str = "Test Developer",
    ) -> dict[str, Any]:
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": full_name},
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _register_user


@pytest.fixture
async def auth_headers(
    register_user: Callable[..., Awaitable[dict[str, Any]]],
) -> dict[str, str]:
    account = await register_user()
    return {"Authorization": f"Bearer {account['access_token']}"}


@pytest.fixture
async def create_application(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> Callable[..., Awaitable[dict[str, Any]]]:
    async def _create_application(**overrides: Any) -> dict[str, Any]:
        payload = {
            "company_name": "Acme Labs",
            "job_title": "Backend Engineer",
            "job_url": "https://jobs.example.com/acme/backend",
            "location": "Berlin",
            "remote_type": "remote",
            "salary_min": 85000,
            "salary_max": 120000,
            "currency": "EUR",
            "status": "applied",
            "source": "Wellfound",
            "notes": "Strong product engineering role.",
            "applied_at": "2026-04-20",
            "follow_up_date": "2026-04-28",
        }
        payload.update(overrides)
        response = await client.post(
            "/api/v1/applications",
            headers=auth_headers,
            json=payload,
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _create_application
