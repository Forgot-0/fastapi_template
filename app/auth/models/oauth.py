from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_model import BaseModel, DateMixin

if TYPE_CHECKING:
    from app.auth.models.user import User


class OAuthProviderEnum(Enum):
    YANDEX = "yandex"
    GOOGLE = "google"
    GITHUB = "github"


class OAuthAccount(BaseModel, DateMixin):
    __tablename__ = "oauth_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    provider: Mapped[OAuthProviderEnum] = mapped_column(SQLEnum(OAuthProviderEnum), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String, nullable=False)
    provider_email: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="cascade", onupdate="cascade"))
    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")

