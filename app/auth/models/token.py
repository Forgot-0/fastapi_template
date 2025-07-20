from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_model import BaseModel


class Token(BaseModel):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jti: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    device_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped['User'] = relationship("User", back_populates="tokens") # type: ignore

    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at or not self.is_revoked

