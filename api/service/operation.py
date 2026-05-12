from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..core.config import get_settings
from ..models import Group, GroupMember, User, utc_now
from ..schemas import operation as schema
from .auth import get_user_by_username


JST = timezone(timedelta(hours=9))
settings = get_settings()

STATUS = {
    "ok": {"label": "元気", "emoji": "😊"},
    "busy": {"label": "忙しい", "emoji": "⚡"},
    "home": {"label": "在宅", "emoji": "🏠"},
    "out": {"label": "外出中", "emoji": "🚶"},
    "sleep": {"label": "就寝", "emoji": "😴"},
    "sos": {"label": "SOS", "emoji": "🆘"},
}

AVATAR_COLORS = [
    ("bg-blue-100", "text-blue-800"),
    ("bg-green-100", "text-green-800"),
    ("bg-pink-100", "text-pink-800"),
    ("bg-amber-100", "text-amber-800"),
    ("bg-purple-100", "text-purple-800"),
]


def format_elapsed_time(updated_at: datetime) -> str:
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=JST)
    now = datetime.now(updated_at.tzinfo)
    seconds = max(0, int((now - updated_at).total_seconds()))

    if seconds < 60:
        return "今"
    if seconds < 3600:
        return f"{seconds // 60}分前"
    if seconds < 86400:
        return f"{seconds // 3600}時間前"
    return f"{seconds // 86400}日前"


def _status_info(status_value: str) -> dict[str, str]:
    return STATUS.get(status_value, STATUS["ok"])


def _avatar_for_user(user_id: int) -> tuple[str, str]:
    return AVATAR_COLORS[user_id % len(AVATAR_COLORS)]


def user_search_response(user: User) -> schema.UserSearchResponse:
    return schema.UserSearchResponse(
        id=user.id,
        username=user.username,
        name=user.display_name,
        display_name=user.display_name,
        email=user.email,
    )


def member_to_response(member: GroupMember) -> schema.GroupMemberResponse:
    user = member.user
    status_info = _status_info(user.current_status)
    avatar_bg, avatar_text = _avatar_for_user(user.id)
    display_name = user.display_name or user.username

    return schema.GroupMemberResponse(
        id=member.id,
        user_id=user.id,
        username=user.username,
        name=display_name,
        display_name=display_name,
        initial=(display_name or user.username)[:1],
        avatar_bg=avatar_bg,
        avatar_text=avatar_text,
        role=member.role,
        status=user.current_status,
        status_label=status_info["label"],
        status_emoji=status_info["emoji"],
        updated_at=user.status_updated_at,
        time=format_elapsed_time(user.status_updated_at),
    )


def group_to_response(group: Group) -> schema.GroupResponse:
    return schema.GroupResponse(
        id=group.id,
        name=group.name,
        emoji=group.emoji,
        color=group.color,
        owner_id=group.owner_id,
        members=[member_to_response(member) for member in group.members],
    )


def _group_query(group_id: int):
    return (
        select(Group)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .where(Group.id == group_id)
    )


def get_group_model(db: Session, group_id: int) -> Group:
    group = db.scalar(_group_query(group_id))
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="グループが存在しません",
        )
    return group


def require_group_member(db: Session, group_id: int, user_id: int) -> GroupMember:
    membership = db.scalar(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このグループのメンバーではありません",
        )
    return membership


def require_group_owner(db: Session, group_id: int, user_id: int) -> Group:
    group = get_group_model(db, group_id)
    if group.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="グループの管理者のみ実行できます",
        )
    return group


def get_my_groups(db: Session, user_id: int) -> list[schema.GroupResponse]:
    groups = db.scalars(
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .where(GroupMember.user_id == user_id)
        .order_by(Group.updated_at.desc(), Group.id.desc())
    ).all()
    return [group_to_response(group) for group in groups]


def get_group_by_id(
    db: Session,
    group_id: int,
    current_user: User,
) -> schema.GroupResponse:
    require_group_member(db, group_id, current_user.id)
    return group_to_response(get_group_model(db, group_id))


def create_group(
    db: Session,
    current_user: User,
    payload: schema.CreateGroup,
) -> schema.GroupResponse:
    group = Group(
        name=payload.name.strip(),
        emoji=payload.emoji.strip(),
        color=payload.color.strip(),
        owner_id=current_user.id,
    )
    db.add(group)
    db.flush()

    db.add(
        GroupMember(
            group_id=group.id,
            user_id=current_user.id,
            role="owner",
        )
    )
    db.commit()

    return group_to_response(get_group_model(db, group.id))


def add_member(
    db: Session,
    group_id: int,
    current_user: User,
    payload: schema.AddMemberRequest,
) -> schema.GroupMemberResponse:
    group = require_group_owner(db, group_id, current_user.id)
    target_user = get_user_by_username(db, payload.username)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが存在しません",
        )

    existing = db.scalar(
        select(GroupMember).where(
            GroupMember.group_id == group.id,
            GroupMember.user_id == target_user.id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザーはすでにグループに参加しています",
        )

    member = GroupMember(
        group_id=group.id,
        user_id=target_user.id,
        role="member",
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    member.user = target_user
    return member_to_response(member)


def remove_member(
    db: Session,
    group_id: int,
    current_user: User,
    username: str,
) -> schema.MessageResponse:
    group = require_group_owner(db, group_id, current_user.id)
    target_user = get_user_by_username(db, username)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが存在しません",
        )
    if target_user.id == group.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理者はメンバー削除では削除できません",
        )

    membership = db.scalar(
        select(GroupMember).where(
            GroupMember.group_id == group.id,
            GroupMember.user_id == target_user.id,
        )
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="メンバーが存在しません",
        )

    db.delete(membership)
    db.commit()
    return schema.MessageResponse(message="メンバーを削除しました")


def leave_group(
    db: Session,
    group_id: int,
    current_user: User,
) -> schema.MessageResponse:
    group = get_group_model(db, group_id)
    membership = require_group_member(db, group_id, current_user.id)
    member_count = db.scalar(
        select(func.count(GroupMember.id)).where(GroupMember.group_id == group_id)
    )

    if group.owner_id == current_user.id and member_count and member_count > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理者は他のメンバーがいる間は退会できません",
        )

    if group.owner_id == current_user.id:
        db.delete(group)
        db.commit()
        return schema.MessageResponse(message="グループを削除して退会しました")

    db.delete(membership)
    db.commit()
    return schema.MessageResponse(message="グループから退会しました")


def delete_group(
    db: Session,
    group_id: int,
    current_user: User,
) -> schema.MessageResponse:
    group = require_group_owner(db, group_id, current_user.id)
    db.delete(group)
    db.commit()
    return schema.MessageResponse(message="グループを削除しました")


def get_user_group_ids(db: Session, user_id: int) -> list[int]:
    return list(
        db.scalars(
            select(GroupMember.group_id)
            .where(GroupMember.user_id == user_id)
            .order_by(GroupMember.group_id)
        )
    )


def status_response(db: Session, user: User) -> schema.StatusResponse:
    status_info = _status_info(user.current_status)
    return schema.StatusResponse(
        user_id=user.id,
        username=user.username,
        status=user.current_status,
        status_label=status_info["label"],
        status_emoji=status_info["emoji"],
        updated_at=user.status_updated_at,
        time=format_elapsed_time(user.status_updated_at),
        group_ids=get_user_group_ids(db, user.id),
    )


def update_status(
    db: Session,
    current_user: User,
    payload: schema.UpdateState,
) -> schema.StatusResponse:
    current_user.current_status = payload.status
    current_user.status_updated_at = utc_now()
    db.commit()
    db.refresh(current_user)
    return status_response(db, current_user)


def get_member_status_for_group(
    db: Session,
    group_id: int,
    user_id: int,
) -> schema.GroupMemberResponse:
    membership = db.scalar(
        select(GroupMember)
        .options(selectinload(GroupMember.user))
        .where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="メンバーが存在しません",
        )
    return member_to_response(membership)


def create_invite_link(
    db: Session,
    group_id: int,
    current_user: User,
) -> schema.InviteLinkResponse:
    group = require_group_owner(db, group_id, current_user.id)

    return schema.InviteLinkResponse(
        group_id=group.id,
        invite_link=f"{settings.frontend_url}/invite/{group.id}",
        message=f"「{group.name}」の招待リンクを発行しました",
    )


def search_users(
    users: list[User],
) -> list[schema.UserSearchResponse]:
    return [user_search_response(user) for user in users]
