from dataclasses import dataclass
from typing import Any, TYPE_CHECKING
import orjson
from sqlalchemy import Boolean, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_model import BaseModel, DateMixin, SoftDeleteMixin
from app.core.events.event import BaseEvent

if TYPE_CHECKING:
    from app.auth.models.role import Role
    from app.auth.models.session import Session


@dataclass(frozen=True)
class CreatedUserEvent(BaseEvent):
    email: str
    username: str

    __event_name__: str = "user_created"



class User(BaseModel, DateMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    jwt_data: Mapped[bytes | None] = mapped_column(LargeBinary)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    sessions: Mapped[list['Session']] = relationship(
        back_populates='user',
        cascade="all, delete-orphan"
    )

    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )


    @classmethod
    def create(cls, email: str, username: str, password_hash: str, roles: list['Role']) -> "User":
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
            roles = roles
        )
        user.set_jwt_data()

        user.register_event(
            CreatedUserEvent(
                email=email,
                username=username
            )
        )
        return user

    def add_role(self, role: 'Role') -> None:
        self.roles.append(role)
        self.set_jwt_data()

    def set_jwt_data(self, device_id: str | None = None) -> None:
        security_lvl = 999
        permissions = set()
        roles = set()

        for role in self.roles:
            roles.add(role.name)

            security_lvl = min(security_lvl, role.security_level)

            for permission in role.permissions:
                permissions.add(permission.name)

        data: dict[str, Any] = {
            "sub": self.id,
            "roles": list(roles),
            "permissions": list(permissions),
            "lvl": security_lvl,
        }

        if device_id is not None:
            data['sda'] = device_id

        self.jwt_data = orjson.dumps(data)

    def password_reset(self, password_hash: str) -> None:
        self.password_hash = password_hash

    def verify(self) -> None:
        self.is_verified = True