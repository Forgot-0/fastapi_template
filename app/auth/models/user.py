from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_model import BaseModel, DateMixin, SoftDeleteMixin
from app.core.events.event import BaseEvent

if TYPE_CHECKING:
    from app.auth.models.oauth import OAuthAccount
    from app.auth.models.permission import Permission
    from app.auth.models.role import Role
    from app.auth.models.session import Session


@dataclass(frozen=True)
class CreatedUserEvent(BaseEvent):
    email: str
    username: str

    __event_name__: str = "auth.user.created"

    def get_partition_key(self) -> str:
        return str(self.username)


@dataclass(frozen=True)
class VerifiedUserEvent(BaseEvent):
    user_id: int
    username: str
    email: str

    __event_name__: str = "auth.user.verified"

    def get_partition_key(self) -> str:
        return str(self.user_id)



class UserPermissions(BaseModel):
    __tablename__ = "user_permissions"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("permissions.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True,
    )


class User(BaseModel, DateMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    roles: Mapped[set["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
    )

    permissions: Mapped[set["Permission"]] = relationship(
        "Permission", secondary="user_permissions", back_populates="users"
    )

    @classmethod
    def create(
        cls, email: str, username: str, password_hash: str | None,
        roles: set["Role"], is_verified: bool=False
    ) -> "User":
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
            roles=roles,
            is_active=True,
            is_verified=is_verified,
            permissions=set()
        )

        user.register_event(
            CreatedUserEvent(
                email=email,
                username=username
            )
        )
        return user

    @classmethod
    def create_oauth(cls, email: str, username: str, roles: set["Role"]) -> "User":
        return User.create(
            email, username=username, password_hash=None,
            roles=roles, is_verified=True
        )


    def add_role(self, role: "Role") -> None:
        self.roles.add(role)

    def delete_role(self, role: "Role") -> None:
        self.roles.remove(role)

    def add_permission(self, permission: "Permission") -> None:
        self.permissions.add(permission)

    def delete_permission(self, permission: "Permission") -> None:
        self.permissions.remove(permission)

    def password_reset(self, password_hash: str) -> None:
        self.password_hash = password_hash

    def verify(self) -> None:
        self.is_verified = True
        self.register_event(
            VerifiedUserEvent(
                user_id=self.id,
                username=self.username,
                email=self.email
            )
        )

    def get_highest_role(self) -> "Role":
        return max(self.roles, key=lambda r: r.security_level)

    def has_permission(self, permission: "Permission") -> bool:
        return any(role.has_permission(permission) for role in self.roles) or permission in self.permissions

    def get_all_permissions_with_inheritance(self) -> set["Permission"]:
        all_permissions = set()
        for role in self.roles:
            all_permissions.update(role.permissions)
        all_permissions.update(self.permissions)
        return all_permissions

    def can_manage_user(self, target_user: "User") -> bool:
        my_highest_role = self.get_highest_role()
        target_highest_role = target_user.get_highest_role()

        if not my_highest_role or not target_highest_role:
            return False

        return my_highest_role.security_level > target_highest_role.security_level

