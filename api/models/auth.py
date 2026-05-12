from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base, utc_now


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_status: Mapped[str] = mapped_column(String(20), nullable=False, default="ok")
    status_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    memberships = relationship(
        "GroupMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    owned_groups = relationship(
        "Group",
        back_populates="owner",
        foreign_keys="Group.owner_id",
    )


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_oauth_provider_subject",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    user: Mapped[User] = relationship("User", back_populates="oauth_accounts")
