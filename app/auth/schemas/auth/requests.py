from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field

from app.auth.schemas.base import PasswordMixinSchema


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    device_id: str = Field(default_factory=lambda: str(uuid4()), description="Device ID")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token for user")


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token for logout")


class SendVerifyCodeRequest(BaseModel):
    email: EmailStr = Field(..., description="Email for verification")


class SendResetPasswordCodeRequest(BaseModel):
    email: EmailStr = Field(..., description="Email for reset password")


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., description="Токен verification email")


class ResetPasswordRequest(PasswordMixinSchema):
    token: str = Field(..., description="Token for reset password")


class CallbackRequest(BaseModel):
    code: str
    state: str

class OAuthCallbackQuery(BaseModel):
    provider: str
    code: str
    state: str
