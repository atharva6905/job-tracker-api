from fastapi.testclient import TestClient

from app.models.application import ApplicationStatus


def _create_company(client: TestClient, headers: dict[str, str], name: str) -> dict:
    response = client.post("/companies/", json={"name": name}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def _create_application(
    client: TestClient,
    headers: dict[str, str],
    company_id: int,
    role: str,
    status: str = ApplicationStatus.Applied.value,
) -> dict:
    response = client.post(
        "/applications/",
        json={
            "company_id": company_id,
            "role": role,
            "status": status,
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_application(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("app1@example.com", "password123")
    headers = auth_headers("app1@example.com", "password123")
    company = _create_company(client, headers, "Acme")

    response = client.post(
        "/applications/",
        json={
            "company_id": company["id"],
            "role": "Backend Engineer",
            "status": ApplicationStatus.Applied.value,
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "Backend Engineer"
    assert data["status"] == ApplicationStatus.Applied.value


def test_create_application_under_other_users_company_fails(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("app2a@example.com", "password123")
    make_user("app2b@example.com", "password123")
    headers_a = auth_headers("app2a@example.com", "password123")
    headers_b = auth_headers("app2b@example.com", "password123")
    company = _create_company(client, headers_a, "Private Co")

    response = client.post(
        "/applications/",
        json={
            "company_id": company["id"],
            "role": "Unauthorized Role",
            "status": ApplicationStatus.Applied.value,
        },
        headers=headers_b,
    )

    assert response.status_code == 404


def test_list_applications_returns_only_own(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("app3a@example.com", "password123")
    make_user("app3b@example.com", "password123")
    headers_a = auth_headers("app3a@example.com", "password123")
    headers_b = auth_headers("app3b@example.com", "password123")

    company_a = _create_company(client, headers_a, "Alpha Co")
    company_b = _create_company(client, headers_b, "Beta Co")
    app_a = _create_application(client, headers_a, company_a["id"], "Role A")
    app_b = _create_application(client, headers_b, company_b["id"], "Role B")

    response_a = client.get("/applications/", headers=headers_a)
    response_b = client.get("/applications/", headers=headers_b)

    assert response_a.status_code == 200
    assert response_b.status_code == 200
    assert [item["id"] for item in response_a.json()["items"]] == [app_a["id"]]
    assert [item["id"] for item in response_b.json()["items"]] == [app_b["id"]]


def test_pagination(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("app4@example.com", "password123")
    headers = auth_headers("app4@example.com", "password123")
    company = _create_company(client, headers, "Pagination Co")

    for index in range(5):
        _create_application(client, headers, company["id"], f"Role {index}")

    response = client.get("/applications/?page=1&limit=2", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5


def test_filter_by_status(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("app5@example.com", "password123")
    headers = auth_headers("app5@example.com", "password123")
    company = _create_company(client, headers, "Status Co")

    _create_application(
        client,
        headers,
        company["id"],
        "Applied Role",
        ApplicationStatus.Applied.value,
    )
    interview_app = _create_application(
        client,
        headers,
        company["id"],
        "Interview Role",
        ApplicationStatus.Interview.value,
    )

    response = client.get(
        f"/applications/?status={ApplicationStatus.Interview.value}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == interview_app["id"]
    assert data["items"][0]["status"] == ApplicationStatus.Interview.value


def test_filter_by_company_id(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("app6@example.com", "password123")
    headers = auth_headers("app6@example.com", "password123")
    company_a = _create_company(client, headers, "Company A")
    company_b = _create_company(client, headers, "Company B")
    app_a = _create_application(client, headers, company_a["id"], "Role A")
    _create_application(client, headers, company_b["id"], "Role B")

    response = client.get(
        f"/applications/?company_id={company_a['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == app_a["id"]
    assert data["items"][0]["company_id"] == company_a["id"]


def test_invalid_status_transition(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("app7@example.com", "password123")
    headers = auth_headers("app7@example.com", "password123")
    company = _create_company(client, headers, "Transition Co")
    application = _create_application(client, headers, company["id"], "Engineer")

    response = client.patch(
        f"/applications/{application['id']}",
        json={"status": ApplicationStatus.Offer.value},
        headers=headers,
    )

    assert response.status_code == 400


def test_valid_status_transition(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("app8@example.com", "password123")
    headers = auth_headers("app8@example.com", "password123")
    company = _create_company(client, headers, "Progression Co")
    application = _create_application(client, headers, company["id"], "Engineer")

    first_response = client.patch(
        f"/applications/{application['id']}",
        json={"status": ApplicationStatus.Interview.value},
        headers=headers,
    )
    second_response = client.patch(
        f"/applications/{application['id']}",
        json={"status": ApplicationStatus.Offer.value},
        headers=headers,
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == ApplicationStatus.Interview.value
    assert second_response.status_code == 200
    assert second_response.json()["status"] == ApplicationStatus.Offer.value
