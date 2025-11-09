from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_model import BaseModel, DateMixin
from app.auth.models.permission import Permission

if TYPE_CHECKING:
    from app.auth.models.user import User


class UserRoles(BaseModel):
    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True,
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True,
        nullable=False,
    )


class Role(BaseModel, DateMixin):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), index=True, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(256))
    security_level: Mapped[int] = mapped_column(
        nullable=False, default=1
    )

    users: Mapped[list["User"]] = relationship(
        argument="User", secondary="user_roles", back_populates="roles"
    )

    permissions: Mapped[set["Permission"]] = relationship(
        "Permission", secondary="role_permissions", back_populates="roles"
    )

    def add_permission(self, permission: Permission) -> None:
        self.permissions.add(permission)

    def delete_permission(self, permission: Permission) -> None:
        if permission not in self.permissions:
            return

        self.permissions.remove(permission)

    def update(
        self,
        name: str | None=None,
        description: str | None=None,
        security_level: int | None=None
    ) -> None:
        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        if security_level is not None:
            self.security_level = security_level