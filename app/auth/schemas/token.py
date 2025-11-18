from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "reset_password_token"
    EMAIL_CHANGE = "email_change_token"
    OAUTH_CONNECT = "oauth_connect_state"


class TokenGroup(BaseModel):
    refresh_token: str
    access_token: str


class Token(BaseModel):
    type: str
    sub: str
    lvl: int
    jti: str
    did: str
    exp: float
    iat: float
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class DeviceInformation(BaseModel):
    user_agent: str
    device_id: str
    device_info: bytes


class DeviceInfo(BaseModel):
    browser_family: str
    os_family: str
    device: str


class OAuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int | None = Field(None)
    refresh_token: str | None = Field(None)
    scope: str | None = Field(None)


class OAuthData(BaseModel):
    provider_user_id: str
    email: EmailStr
    username: str | None = Field(None)