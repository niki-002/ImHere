from datetime import datetime
from typing import Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


OAuthProvider = Literal["google", "apple"]


class LoginRegister(BaseModel):
    username: str = Field(
        ...,
        validation_alias=AliasChoices("username", "name"),
        min_length=1,
        max_length=50,
    )
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    display_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("displayName", "display_name"),
        max_length=100,
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return str(value).strip().lower()


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return str(value).strip().lower()


class OAuthLoginRequest(BaseModel):
    id_token: str = Field(..., validation_alias=AliasChoices("idToken", "id_token"))
    username: str | None = Field(default=None, min_length=1, max_length=50)
    display_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("displayName", "display_name", "name"),
        max_length=100,
    )

    model_config = ConfigDict(populate_by_name=True)


class LoginUserResponse(BaseModel):
    id: int
    username: str
    name: str
    display_name: str = Field(alias="displayName")
    email: str | None
    status: str
    status_updated_at: datetime = Field(alias="statusUpdatedAt")

    model_config = ConfigDict(populate_by_name=True)


class LoginTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUserResponse
