from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from ..db import SessionLocal, get_db
from ..models import User
from ..schemas import operation as schema
from ..service import auth as auth_service
from ..service import operation as service


router = APIRouter(tags=["operation"])


class GroupConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, group_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[group_id].add(websocket)

    def disconnect(self, group_id: int, websocket: WebSocket) -> None:
        self.active_connections[group_id].discard(websocket)
        if not self.active_connections[group_id]:
            self.active_connections.pop(group_id, None)

    async def broadcast(self, group_id: int, message: dict) -> None:
        for websocket in list(self.active_connections.get(group_id, set())):
            try:
                await websocket.send_json(message)
            except RuntimeError:
                self.disconnect(group_id, websocket)


manager = GroupConnectionManager()


@router.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello, World!"}


@router.get("/groups", response_model=list[schema.GroupResponse])
def get_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> list[schema.GroupResponse]:
    return service.get_my_groups(db, current_user.id)


@router.get("/groups/{group_id}", response_model=schema.GroupResponse)
def read_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> schema.GroupResponse:
    return service.get_group_by_id(db, group_id, current_user)


@router.post("/groups", response_model=schema.GroupResponse)
def create_group(
    payload: schema.CreateGroup,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> schema.GroupResponse:
    return service.create_group(db, current_user, payload)


@router.post("/groups/{group_id}/members", response_model=schema.GroupMemberResponse)
def add_member(
    group_id: int,
    payload: schema.AddMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> schema.GroupMemberResponse:
    return service.add_member(db, group_id, current_user, payload)


@router.delete("/groups/{group_id}/members/{username}", response_model=schema.MessageResponse)
def remove_member(
    group_id: int,
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> schema.MessageResponse:
    return service.remove_member(db, group_id, current_user, username)


@router.delete("/groups/{group_id}/leave", response_model=schema.MessageResponse)
def leave_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> schema.MessageResponse:
    return service.leave_group(db, group_id, current_user)


@router.delete("/groups/{group_id}", response_model=schema.MessageResponse)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> schema.MessageResponse:
    return service.delete_group(db, group_id, current_user)


@router.post("/groups/{group_id}/invite", response_model=schema.InviteLinkResponse)
def invite_link(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> schema.InviteLinkResponse:
    return service.create_invite_link(db, group_id, current_user)


@router.get("/status", response_model=schema.StatusResponse)
def get_my_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> schema.StatusResponse:
    return service.status_response(db, current_user)


@router.patch("/status", response_model=schema.StatusResponse)
async def patch_my_status(
    payload: schema.UpdateState,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> schema.StatusResponse:
    response = service.update_status(db, current_user, payload)
    response_payload = response.model_dump(by_alias=True, mode="json")

    for group_id in response.group_ids:
        member = service.get_member_status_for_group(db, group_id, current_user.id)
        await manager.broadcast(
            group_id,
            {
                "type": "status.updated",
                "groupId": group_id,
                "status": response_payload,
                "member": member.model_dump(by_alias=True, mode="json"),
            },
        )

    return response


@router.get("/users/search", response_model=list[schema.UserSearchResponse])
def search_users(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_login_user),
) -> list[schema.UserSearchResponse]:
    del current_user
    return service.search_users(auth_service.search_users_by_name(db, name))


@router.websocket("/ws/groups/{group_id}")
async def group_status_websocket(websocket: WebSocket, group_id: int) -> None:
    token = (
        websocket.query_params.get("token")
        or websocket.cookies.get("access_token")
        or websocket.cookies.get("login_token")
    )
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = SessionLocal()
    try:
        user = auth_service.get_user_from_token(db, token)
        service.require_group_member(db, group_id, user.id)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    finally:
        db.close()

    await manager.connect(group_id, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            if message == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(group_id, websocket)
