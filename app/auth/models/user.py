from dataclasses import dataclass
from typing import Any
import orjson
from sqlalchemy import Boolean, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_model import BaseModel, DateMixin, SoftDeleteMixin
from app.core.events.event import BaseEvent


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

    sessions: Mapped[list['Session']] = relationship(back_populates='user', cascade="all, delete-orphan") # type: ignore

    @classmethod
    def create(cls, email: str, username: str, password_hash: str) -> "User":
        user = User(
            email=email,
            username=username,
            password_hash=password_hash
        )
        user.set_jwt_data()

        user.register_event(
            CreatedUserEvent(
                email=email,
                username=username
            )
        )
        return user

    def set_jwt_data(self, device_id: str | None = None) -> None:
        security_lvl = 1
        data: dict[str, Any] = {
            "sub": self.id,
            "lvl": security_lvl,
        }

        if device_id is not None:
            data['sda'] = device_id

        self.jwt_data = orjson.dumps(data)

    def password_reset(self, password_hash: str) -> None:
        self.password_hash = password_hash

    def verify(self) -> None:
        self.is_verified = True