from httpx import AsyncClient


async def test_register_login_and_current_user(client: AsyncClient) -> None:
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alex@example.com",
            "password": "SecurePass123!",
            "full_name": "Alex Remote",
        },
    )
    assert register_response.status_code == 201
    registered = register_response.json()
    assert registered["token_type"] == "bearer"
    assert registered["user"]["email"] == "alex@example.com"

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "alex@example.com", "password": "SecurePass123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "alex@example.com"


async def test_register_rejects_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "SecurePass123!",
        "full_name": "Duplicate User",
    }
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201

    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "conflict"
