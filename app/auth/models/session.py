from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_model import BaseModel
from app.core.utils import now_utc


class Session(BaseModel):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jti: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    device_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    user_agent: Mapped[str] = mapped_column(String, nullable=True)
    ip: Mapped[str] = mapped_column(String, nullable=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    last_activity: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped['User'] = relationship("User", back_populates="sessions") # type: ignore

    def is_valid(self) -> bool:
        return now_utc() < self.expires_at and not self.is_revoked