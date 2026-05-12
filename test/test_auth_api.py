from fastapi.testclient import TestClient


def test_register_returns_token_and_normalized_user(
    client: TestClient,
    unique_username,
) -> None:
    username = unique_username("alice")

    response = client.post(
        "/auth/register",
        json={
            "username": f" {username.upper()} ",
            "email": f" {username.upper()}@example.COM ",
            "password": "password123",
            "displayName": "Alice A.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == username
    assert data["user"]["email"] == f"{username}@example.com"
    assert data["user"]["displayName"] == "Alice A."
    assert data["user"]["status"] == "ok"
    assert data["user"]["statusUpdatedAt"]


def test_register_rejects_duplicate_email_and_username(
    client: TestClient,
    register_user,
    unique_username,
) -> None:
    username = unique_username("alice")
    email = f"{username}@example.com"
    register_user(username, email)

    duplicate_email = client.post(
        "/auth/register",
        json={
            "username": unique_username("alice2"),
            "email": email.upper(),
            "password": "password123",
        },
    )
    duplicate_username = client.post(
        "/auth/register",
        json={
            "username": username.upper(),
            "email": f"{unique_username('alice2')}@example.com",
            "password": "password123",
        },
    )

    assert duplicate_email.status_code == 400
    assert duplicate_email.json()["detail"] == "このメールアドレスはすでに使われています"
    assert duplicate_username.status_code == 400
    assert duplicate_username.json()["detail"] == "このユーザー名はすでに使われています"


def test_login_and_auth_me_with_bearer_token(
    client: TestClient,
    register_user,
    auth_headers,
    unique_username,
) -> None:
    username = unique_username("alice")
    register_user(
        username,
        f"{username}@example.com",
        password="correct-password",
        display_name="Alice",
    )

    login = client.post(
        "/auth/login",
        json={
            "email": f" {username.upper()}@example.com ",
            "password": "correct-password",
        },
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/auth/me", headers=auth_headers(token))

    assert me.status_code == 200
    assert me.json()["username"] == username
    assert me.json()["displayName"] == "Alice"


def test_login_rejects_invalid_password(
    client: TestClient,
    register_user,
    unique_username,
) -> None:
    username = unique_username("alice")
    register_user(username, f"{username}@example.com", password="correct-password")

    response = client.post(
        "/auth/login",
        json={"email": f"{username}@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "メールアドレスまたはパスワードが違います"


def test_current_user_requires_authentication(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "ログインが必要です"


def test_oauth_login_creates_user_without_external_jwks(
    client: TestClient,
    monkeypatch,
    unique_username,
) -> None:
    from api.service import auth as auth_service

    username = unique_username("oauth")
    subject = f"google-{username}"

    def fake_verify_oauth_id_token(provider: str, id_token: str) -> dict:
        assert provider == "google"
        assert id_token == "test-id-token"
        return {
            "sub": subject,
            "email": f"{username}@example.com",
            "email_verified": True,
            "name": "OAuth User",
            "preferred_username": username,
            "iss": "https://accounts.google.com",
        }

    monkeypatch.setattr(
        auth_service,
        "verify_oauth_id_token",
        fake_verify_oauth_id_token,
    )

    first_login = client.post(
        "/auth/oauth/google",
        json={"idToken": "test-id-token"},
    )
    second_login = client.post(
        "/auth/google",
        json={"idToken": "test-id-token"},
    )

    assert first_login.status_code == 200, first_login.text
    assert second_login.status_code == 200, second_login.text
    assert first_login.json()["user"]["id"] == second_login.json()["user"]["id"]
    assert first_login.json()["user"]["username"] == username


def test_oauth_login_links_existing_user_by_verified_email(
    client: TestClient,
    register_user,
    monkeypatch,
    unique_username,
) -> None:
    from api.service import auth as auth_service

    username = unique_username("linked")
    register_user(username, f"{username}@example.com", display_name="Existing User")

    monkeypatch.setattr(
        auth_service,
        "verify_oauth_id_token",
        lambda provider, id_token: {
            "sub": f"{provider}-{username}",
            "email": f"{username.upper()}@example.com",
            "email_verified": "true",
            "name": "OAuth Name",
            "iss": "https://accounts.google.com",
        },
    )

    response = client.post(
        "/auth/google",
        json={"idToken": "test-id-token"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["user"]["username"] == username
    assert response.json()["user"]["displayName"] == "Existing User"
