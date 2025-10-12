from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


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
    roles: list[str]
    permissions: list[str] = Field(default_factory=list)


class DeviceInformation(BaseModel):
    user_agent: str
    device_id: str
    device_info: bytes


class DeviceInfo(BaseModel):
    browser_family: str
    os_family: str
    device: str
