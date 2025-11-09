from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_model import BaseModel

if TYPE_CHECKING:
    from app.auth.models.user import User


class Session(BaseModel):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    device_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    device_info: Mapped[bytes] = mapped_column(LargeBinary)
    user_agent: Mapped[str] = mapped_column(String)

    last_activity: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped['User'] = relationship("User", back_populates="sessions")

    def deactivate(self) -> None:
        self.is_active = False