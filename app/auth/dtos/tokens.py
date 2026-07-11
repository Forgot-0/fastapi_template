from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.models.oauth import OAuthProviderEnum


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"
    EMAIL_CHANGE = "email_change_token"
    OAUTH_CONNECT = "oauth_connect_state"


class TokenGroup(BaseModel):
    refresh_token: str
    access_token: str


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


class OAuthAccountDTO(BaseModel):
    id: int
    user_id: int

    provider: OAuthProviderEnum
    provider_user_id: int
    provider_email: str
    
    is_active: bool    

    model_config = ConfigDict(from_attributes=True)
