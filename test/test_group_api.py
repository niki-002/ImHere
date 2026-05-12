from fastapi.testclient import TestClient


def test_group_endpoints_require_authentication(client: TestClient) -> None:
    list_response = client.get("/groups")
    create_response = client.post(
        "/groups",
        json={"name": "Family", "emoji": "home", "color": "bg-blue-50"},
    )

    assert list_response.status_code == 401
    assert create_response.status_code == 401


def test_create_list_and_read_group(
    client: TestClient,
    register_user,
    auth_headers,
    create_group,
    unique_username,
) -> None:
    owner = register_user(unique_username("owner"), display_name="Owner")
    token = owner["access_token"]

    group = create_group(
        token,
        name="Family Room",
        emoji="home",
        color="bg-red-50",
    )
    list_response = client.get("/groups", headers=auth_headers(token))
    detail_response = client.get(
        f"/groups/{group['id']}",
        headers=auth_headers(token),
    )

    assert group["name"] == "Family Room"
    assert group["ownerId"] == owner["user"]["id"]
    assert group["members"][0]["username"] == owner["user"]["username"]
    assert group["members"][0]["role"] == "owner"
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [group["id"]]
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == group["id"]


def test_owner_can_add_and_remove_member(
    client: TestClient,
    register_user,
    auth_headers,
    create_group,
    unique_username,
) -> None:
    owner = register_user(unique_username("owner"), display_name="Owner")
    member = register_user(unique_username("member"), display_name="Member")
    outsider = register_user(unique_username("outsider"), display_name="Outsider")
    group = create_group(owner["access_token"])

    forbidden = client.post(
        f"/groups/{group['id']}/members",
        headers=auth_headers(outsider["access_token"]),
        json={"username": member["user"]["username"]},
    )
    add_response = client.post(
        f"/groups/{group['id']}/members",
        headers=auth_headers(owner["access_token"]),
        json={"username": member["user"]["username"]},
    )
    duplicate = client.post(
        f"/groups/{group['id']}/members",
        headers=auth_headers(owner["access_token"]),
        json={"username": member["user"]["username"]},
    )
    member_detail = client.get(
        f"/groups/{group['id']}",
        headers=auth_headers(member["access_token"]),
    )
    remove_response = client.delete(
        f"/groups/{group['id']}/members/{member['user']['username']}",
        headers=auth_headers(owner["access_token"]),
    )
    removed_member_detail = client.get(
        f"/groups/{group['id']}",
        headers=auth_headers(member["access_token"]),
    )

    assert forbidden.status_code == 403
    assert add_response.status_code == 200, add_response.text
    assert add_response.json()["username"] == member["user"]["username"]
    assert add_response.json()["role"] == "member"
    assert duplicate.status_code == 400
    assert member_detail.status_code == 200
    assert remove_response.status_code == 200
    assert remove_response.json()["message"] == "メンバーを削除しました"
    assert removed_member_detail.status_code == 403


def test_owner_cannot_remove_self_as_member(
    client: TestClient,
    register_user,
    auth_headers,
    create_group,
    unique_username,
) -> None:
    owner = register_user(unique_username("owner"), display_name="Owner")
    group = create_group(owner["access_token"])

    response = client.delete(
        f"/groups/{group['id']}/members/{owner['user']['username']}",
        headers=auth_headers(owner["access_token"]),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "管理者はメンバー削除では削除できません"


def test_leave_and_delete_group_rules(
    client: TestClient,
    register_user,
    auth_headers,
    create_group,
    unique_username,
) -> None:
    owner = register_user(unique_username("owner"), display_name="Owner")
    member = register_user(unique_username("member"), display_name="Member")
    group = create_group(owner["access_token"])
    add_response = client.post(
        f"/groups/{group['id']}/members",
        headers=auth_headers(owner["access_token"]),
        json={"username": member["user"]["username"]},
    )
    assert add_response.status_code == 200, add_response.text

    owner_leave = client.delete(
        f"/groups/{group['id']}/leave",
        headers=auth_headers(owner["access_token"]),
    )
    member_leave = client.delete(
        f"/groups/{group['id']}/leave",
        headers=auth_headers(member["access_token"]),
    )
    delete_response = client.delete(
        f"/groups/{group['id']}",
        headers=auth_headers(owner["access_token"]),
    )
    list_response = client.get(
        "/groups",
        headers=auth_headers(owner["access_token"]),
    )

    assert owner_leave.status_code == 400
    assert owner_leave.json()["detail"] == "管理者は他のメンバーがいる間は退会できません"
    assert member_leave.status_code == 200
    assert member_leave.json()["message"] == "グループから退会しました"
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "グループを削除しました"
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_invite_link_requires_owner(
    client: TestClient,
    register_user,
    auth_headers,
    create_group,
    unique_username,
) -> None:
    owner = register_user(unique_username("owner"), display_name="Owner")
    member = register_user(unique_username("member"), display_name="Member")
    group = create_group(owner["access_token"])
    add_response = client.post(
        f"/groups/{group['id']}/members",
        headers=auth_headers(owner["access_token"]),
        json={"username": member["user"]["username"]},
    )
    assert add_response.status_code == 200, add_response.text

    forbidden = client.post(
        f"/groups/{group['id']}/invite",
        headers=auth_headers(member["access_token"]),
    )
    response = client.post(
        f"/groups/{group['id']}/invite",
        headers=auth_headers(owner["access_token"]),
    )

    assert forbidden.status_code == 403
    assert response.status_code == 200
    assert response.json()["groupId"] == group["id"]
    assert response.json()["inviteLink"].endswith(f"/invite/{group['id']}")
