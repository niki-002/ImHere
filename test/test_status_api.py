from fastapi.testclient import TestClient


def test_status_endpoints_require_authentication(client: TestClient) -> None:
    get_response = client.get("/status")
    patch_response = client.patch("/status", json={"status": "busy"})

    assert get_response.status_code == 401
    assert patch_response.status_code == 401


def test_get_status_includes_group_ids(
    client: TestClient,
    register_user,
    auth_headers,
    create_group,
    unique_username,
) -> None:
    user = register_user(unique_username("status"), display_name="Status User")
    group = create_group(user["access_token"])

    response = client.get("/status", headers=auth_headers(user["access_token"]))

    assert response.status_code == 200
    data = response.json()
    assert data["userId"] == user["user"]["id"]
    assert data["username"] == user["user"]["username"]
    assert data["status"] == "ok"
    assert data["groupIds"] == [group["id"]]
    assert data["updatedAt"]
    assert data["time"]


def test_patch_status_updates_current_user(
    client: TestClient,
    register_user,
    auth_headers,
    unique_username,
) -> None:
    user = register_user(unique_username("status"), display_name="Status User")
    headers = auth_headers(user["access_token"])

    response = client.patch("/status", headers=headers, json={"status": "busy"})
    me = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "busy"
    assert response.json()["statusLabel"] == "忙しい"
    assert me.status_code == 200
    assert me.json()["status"] == "busy"


def test_patch_status_rejects_unknown_status(
    client: TestClient,
    register_user,
    auth_headers,
    unique_username,
) -> None:
    user = register_user(unique_username("status"), display_name="Status User")

    response = client.patch(
        "/status",
        headers=auth_headers(user["access_token"]),
        json={"status": "offline"},
    )

    assert response.status_code == 422
