from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Self

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import INET

from app.core.db.base_model import BaseModel
from app.core.events.event import BaseEvent
from app.core.utils import now_utc

if TYPE_CHECKING:
    from app.auth.models.user import User


@dataclass(frozen=True)
class NewSessionEvent(BaseEvent):
    user_id: int
    device_id: str

    __event_name__: str = "auth.session.created"

    def get_partition_key(self) -> str:
        return str(self.user_id)


@dataclass(frozen=True)
class SuspiciousSessionEvent(BaseEvent):
    user_id: int
    session_id: int
    reason: str
    old_value: str | None
    new_value: str | None

    __event_name__: str = "auth.session.suspicious"

    def get_partition_key(self) -> str:
        return str(self.user_id)


class Session(BaseModel):
    __tablename__ = "sessions"
    __table_args__ = (
        Index("idx_sessions_user_device", "user_id", "device_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    device_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    device_info: Mapped[bytes] = mapped_column(LargeBinary)
    user_agent: Mapped[str] = mapped_column(String)

    last_activity: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped["User"] = relationship("User", back_populates="sessions")


    @classmethod
    def create(
        cls,
        user_id: int,
        device_id: str,
        device_info: bytes,
        user_agent: str
    ) -> Self:
        instance = cls(
            user_id=user_id,
            device_id=device_id,
            device_info=device_info,
            user_agent=user_agent,
            is_active=True
        )

        instance.register_event(
            NewSessionEvent(
                user_id=user_id,
                device_id=device_id
            )
        )
        return instance

    def deactivate(self) -> None:
        self.is_active = False
        self.last_activity = now_utc()

    def online(self) -> None:
        self.last_activity = now_utc()
