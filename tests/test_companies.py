from fastapi.testclient import TestClient


def test_create_company(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("company1@example.com", "password123")
    headers = auth_headers("company1@example.com", "password123")

    response = client.post(
        "/companies/",
        json={"name": "Acme", "location": "Toronto", "link": "https://acme.test"},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Acme"


def test_duplicate_company_name_same_user_fails(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("company2@example.com", "password123")
    headers = auth_headers("company2@example.com", "password123")
    payload = {"name": "Acme"}

    first_response = client.post("/companies/", json=payload, headers=headers)
    second_response = client.post("/companies/", json=payload, headers=headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_same_company_name_different_users_ok(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("company3a@example.com", "password123")
    make_user("company3b@example.com", "password123")
    headers_a = auth_headers("company3a@example.com", "password123")
    headers_b = auth_headers("company3b@example.com", "password123")
    payload = {"name": "Shared Name"}

    response_a = client.post("/companies/", json=payload, headers=headers_a)
    response_b = client.post("/companies/", json=payload, headers=headers_b)

    assert response_a.status_code == 201
    assert response_b.status_code == 201


def test_list_companies_returns_only_own(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("company4a@example.com", "password123")
    make_user("company4b@example.com", "password123")
    headers_a = auth_headers("company4a@example.com", "password123")
    headers_b = auth_headers("company4b@example.com", "password123")

    client.post("/companies/", json={"name": "Alpha"}, headers=headers_a)
    client.post("/companies/", json={"name": "Beta"}, headers=headers_a)
    client.post("/companies/", json={"name": "Gamma"}, headers=headers_b)

    response_a = client.get("/companies/", headers=headers_a)
    response_b = client.get("/companies/", headers=headers_b)

    assert response_a.status_code == 200
    assert response_b.status_code == 200
    assert {item["name"] for item in response_a.json()} == {"Alpha", "Beta"}
    assert {item["name"] for item in response_b.json()} == {"Gamma"}


def test_get_other_users_company_returns_404(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("company5a@example.com", "password123")
    make_user("company5b@example.com", "password123")
    headers_a = auth_headers("company5a@example.com", "password123")
    headers_b = auth_headers("company5b@example.com", "password123")

    create_response = client.post(
        "/companies/",
        json={"name": "Private Co"},
        headers=headers_a,
    )
    company_id = create_response.json()["id"]

    response = client.get(f"/companies/{company_id}", headers=headers_b)

    assert response.status_code == 404


def test_update_other_users_company_returns_404(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("company6a@example.com", "password123")
    make_user("company6b@example.com", "password123")
    headers_a = auth_headers("company6a@example.com", "password123")
    headers_b = auth_headers("company6b@example.com", "password123")

    create_response = client.post(
        "/companies/",
        json={"name": "Locked Co"},
        headers=headers_a,
    )
    company_id = create_response.json()["id"]

    response = client.patch(
        f"/companies/{company_id}",
        json={"location": "Ottawa"},
        headers=headers_b,
    )

    assert response.status_code == 404


def test_delete_company(
    client: TestClient,
    make_user,
    auth_headers,
) -> None:
    make_user("company7@example.com", "password123")
    headers = auth_headers("company7@example.com", "password123")

    create_response = client.post(
        "/companies/",
        json={"name": "Delete Me"},
        headers=headers,
    )
    company_id = create_response.json()["id"]

    delete_response = client.delete(f"/companies/{company_id}", headers=headers)
    get_response = client.get(f"/companies/{company_id}", headers=headers)

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
