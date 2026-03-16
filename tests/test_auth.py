from fastapi.testclient import TestClient


def test_register_creates_user(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "user@example.com"
    assert "password" not in data


def test_register_duplicate_email_fails(client: TestClient) -> None:
    payload = {"email": "duplicate@example.com", "password": "password123"}

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_returns_token(
    client: TestClient,
    make_user,
) -> None:
    make_user("login@example.com", "password123")

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_fails(
    client: TestClient,
    make_user,
) -> None:
    make_user("wrongpass@example.com", "password123")

    response = client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_me_requires_auth(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_returns_current_user(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    user = make_user("me@example.com", "password123")
    headers = auth_headers("me@example.com", "password123")

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["email"] == "me@example.com"