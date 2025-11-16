from abc import ABC, abstractmethod
from dataclasses import dataclass
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
    user: Mapped['User'] = relationship("User", back_populates='oauth_accounts')


@dataclass
class OAuthProvider(ABC):
    name: str
    client_id: str
    client_secret: str
    redirect_uri: str
    connect_url: str
    token_url: str
    userinfo_url: str

    @abstractmethod
    def get_auth_url(self) -> str: ...

    @abstractmethod
    def get_connect_url(self) -> str: ...


@dataclass
class OAuthGoogle(OAuthProvider):
    def get_auth_url(self) -> str:
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id="
            f"{self.client_id}&redirect_uri={self.redirect_uri}&scope=openid%20profile%20email&access_type=offline"
        )

    def get_connect_url(self) -> str:
        return (
            "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id="
            f"{self.client_id}&redirect_uri={self.connect_url}&scope=openid%20profile%20email&access_type=offline"
        )


@dataclass
class OAuthYandex(OAuthProvider):
    def get_auth_url(self) -> str:
        return (
            "https://oauth.yandex.ru/authorize?response_type=code&client_id="
            f"{self.client_id}&redirect_uri={self.redirect_uri}"
        )

    def get_connect_url(self) -> str:
        return (
            "https://oauth.yandex.ru/authorize?response_type=code&client_id="
            f"{self.client_id}&redirect_uri={self.connect_url}"
        )


class OAuthGithub(OAuthProvider):
    def get_auth_url(self) -> str:
        return (
            "https://github.com/login/oauth/authorize?client_id="
            f"{self.client_id}&redirect_uri={self.redirect_uri}&scope=read:user,user:email"
        )

    def get_connect_url(self) -> str:
        return (
            "https://github.com/login/oauth/authorize?client_id="
            f"{self.client_id}&redirect_uri={self.connect_url}&scope=read:user,user:email"
        )
