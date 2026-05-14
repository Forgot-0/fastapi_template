from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_model import BaseModel
from app.core.events.event import BaseEvent
from app.core.utils import now_utc

if TYPE_CHECKING:
    from app.auth.models.user import User


@dataclass(frozen=True)
class NewSessionCreatedEvent(BaseEvent):
    user_id: int
    user_agent: str

    __event_name__ = "auth.sessions.created"


class Session(BaseModel):
    __tablename__ = "sessions"
    __table_args__ = (
        Index("idx_sessions_user_device", "user_id", "device_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    device_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    device_info: Mapped[bytes] = mapped_column(LargeBinary)
    user_agent: Mapped[str] = mapped_column(String)

    last_activity: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped["User"] = relationship("User", back_populates="sessions")

    @classmethod
    def create(cls, user_id: int, device_id: str, device_info: bytes, user_agent:  str) -> "Session":
        instance = cls(
            user_id=user_id,
            device_id=device_id,
            device_info=device_info,
            user_agent=user_agent,
            last_activity = now_utc(),
            is_active=True,
        )
        instance.register_event(
            NewSessionCreatedEvent(
                user_id=user_id,
                user_agent=user_agent,
            )
        )
        return instance


    def deactivate(self) -> None:
        self.is_active = False
        self.last_activity = now_utc()

    def online(self) -> None:
        self.last_activity = now_utc()
