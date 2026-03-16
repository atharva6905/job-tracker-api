from fastapi.testclient import TestClient

from app.models.application import ApplicationStatus
from app.models.interview import RoundType


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


def test_create_interview(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("interview1@example.com", "password123")
    headers = auth_headers("interview1@example.com", "password123")
    company = _create_company(client, headers, "Acme")
    application = _create_application(client, headers, company["id"], "Engineer")

    response = client.post(
        f"/applications/{application['id']}/interviews/",
        json={"round_type": RoundType.PhoneScreen.value},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["round_type"] == RoundType.PhoneScreen.value


def test_create_interview_auto_updates_status_to_interview(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("interview2@example.com", "password123")
    headers = auth_headers("interview2@example.com", "password123")
    company = _create_company(client, headers, "Status Co")
    application = _create_application(client, headers, company["id"], "Engineer")

    create_response = client.post(
        f"/applications/{application['id']}/interviews/",
        json={"round_type": RoundType.Technical.value},
        headers=headers,
    )
    get_response = client.get(f"/applications/{application['id']}", headers=headers)

    assert create_response.status_code == 201
    assert get_response.status_code == 200
    assert get_response.json()["status"] == ApplicationStatus.Interview.value


def test_create_interview_on_non_applied_status_does_not_regress(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("interview3@example.com", "password123")
    headers = auth_headers("interview3@example.com", "password123")
    company = _create_company(client, headers, "Stable Co")
    application = _create_application(client, headers, company["id"], "Engineer")

    first_update = client.patch(
        f"/applications/{application['id']}",
        json={"status": ApplicationStatus.Interview.value},
        headers=headers,
    )
    create_response = client.post(
        f"/applications/{application['id']}/interviews/",
        json={"round_type": RoundType.Behavioral.value},
        headers=headers,
    )
    get_response = client.get(f"/applications/{application['id']}", headers=headers)

    assert first_update.status_code == 200
    assert create_response.status_code == 201
    assert get_response.status_code == 200
    assert get_response.json()["status"] == ApplicationStatus.Interview.value


def test_cannot_add_interview_to_other_users_application(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("interview4a@example.com", "password123")
    make_user("interview4b@example.com", "password123")
    headers_a = auth_headers("interview4a@example.com", "password123")
    headers_b = auth_headers("interview4b@example.com", "password123")
    company = _create_company(client, headers_a, "Private Co")
    application = _create_application(client, headers_a, company["id"], "Engineer")

    response = client.post(
        f"/applications/{application['id']}/interviews/",
        json={"round_type": RoundType.Final.value},
        headers=headers_b,
    )

    assert response.status_code == 404


def test_list_interviews(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("interview5@example.com", "password123")
    headers = auth_headers("interview5@example.com", "password123")
    company = _create_company(client, headers, "List Co")
    application = _create_application(client, headers, company["id"], "Engineer")

    first_response = client.post(
        f"/applications/{application['id']}/interviews/",
        json={"round_type": RoundType.PhoneScreen.value},
        headers=headers,
    )
    second_response = client.post(
        f"/applications/{application['id']}/interviews/",
        json={"round_type": RoundType.Technical.value},
        headers=headers,
    )
    list_response = client.get(
        f"/applications/{application['id']}/interviews/",
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert {item["round_type"] for item in list_response.json()} == {
        RoundType.PhoneScreen.value,
        RoundType.Technical.value,
    }
