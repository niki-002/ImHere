from fastapi.testclient import TestClient


def test_user_search_requires_authentication(client: TestClient) -> None:
    response = client.get("/users/search", params={"name": "alice"})

    assert response.status_code == 401


def test_user_search_matches_username(
    client: TestClient,
    register_user,
    auth_headers,
    unique_username,
) -> None:
    viewer = register_user(unique_username("viewer"), display_name="Viewer")
    target_username = unique_username("needle")
    target = register_user(target_username, display_name="Target User")
    register_user(unique_username("other"), display_name="Other User")

    response = client.get(
        "/users/search",
        headers=auth_headers(viewer["access_token"]),
        params={"name": target_username[3:-3]},
    )

    assert response.status_code == 200
    usernames = {user["username"] for user in response.json()}
    assert target["user"]["username"] in usernames


def test_user_search_matches_display_name(
    client: TestClient,
    register_user,
    auth_headers,
    unique_username,
) -> None:
    viewer = register_user(unique_username("viewer"), display_name="Viewer")
    needle = unique_username("displayneedle").replace("_", "")
    target = register_user(
        unique_username("target"),
        display_name=f"Find {needle}",
    )
    register_user(unique_username("other"), display_name="Other User")

    response = client.get(
        "/users/search",
        headers=auth_headers(viewer["access_token"]),
        params={"name": needle.upper()},
    )

    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert users[0]["username"] == target["user"]["username"]
    assert users[0]["displayName"] == f"Find {needle}"
