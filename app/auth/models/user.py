from dataclasses import dataclass
from sqlalchemy import Boolean, Integer, String
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
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    tokens: Mapped[list['Token']] = relationship(back_populates='user') # type: ignore

    @classmethod
    def create(cls, email: str, username: str, password_hash: str) -> "User":
        user = User(
            email=email,
            username=username,
            password_hash=password_hash
        )

        user.register_event(
            CreatedUserEvent(
                email=email,
                username=username
            )
        )
        return user