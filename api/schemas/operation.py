from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


StatusType = Literal["ok", "busy", "home", "out", "sleep", "sos"]
MemberRole = Literal["owner", "member"]


class CreateGroup(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    emoji: str = Field(default="👥", min_length=1, max_length=16)
    color: str = Field(default="bg-blue-50", min_length=1, max_length=50)


class AddMemberRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)


class UpdateState(BaseModel):
    status: StatusType


class UserSearchResponse(BaseModel):
    id: int
    username: str
    name: str
    display_name: str = Field(alias="displayName")
    email: str | None

    model_config = ConfigDict(populate_by_name=True)


class StatusResponse(BaseModel):
    user_id: int = Field(alias="userId")
    username: str
    status: StatusType
    status_label: str = Field(alias="statusLabel")
    status_emoji: str = Field(alias="statusEmoji")
    updated_at: datetime = Field(alias="updatedAt")
    time: str
    group_ids: list[int] = Field(alias="groupIds")

    model_config = ConfigDict(populate_by_name=True)


class GroupMemberResponse(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    username: str
    name: str
    display_name: str = Field(alias="displayName")
    initial: str
    avatar_bg: str = Field(alias="avatarBg")
    avatar_text: str = Field(alias="avatarText")
    role: MemberRole
    status: StatusType
    status_label: str = Field(alias="statusLabel")
    status_emoji: str = Field(alias="statusEmoji")
    updated_at: datetime = Field(alias="updatedAt")
    time: str

    model_config = ConfigDict(populate_by_name=True)


class GroupResponse(BaseModel):
    id: int
    name: str
    emoji: str
    color: str
    owner_id: int = Field(alias="ownerId")
    members: list[GroupMemberResponse]

    model_config = ConfigDict(populate_by_name=True)


class InviteLinkResponse(BaseModel):
    group_id: int = Field(alias="groupId")
    invite_link: str = Field(alias="inviteLink")
    message: str

    model_config = ConfigDict(populate_by_name=True)


class MessageResponse(BaseModel):
    message: str
