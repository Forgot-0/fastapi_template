from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field

from app.auth.schemas.base import PasswordMixinSchema


class LoginRequest(BaseModel):
    """
    Схема запроса для входа пользователя.
    """
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль пользователя")
    device_id: str = Field(default_factory=lambda: str(uuid4()), description="Идентификатор устройства")


class RefreshTokenRequest(BaseModel):
    """
    Схема запроса для обновления access токена.
    """
    refresh_token: str = Field(..., description="Refresh токен пользователя")


class LogoutRequest(BaseModel):
    """
    Схема запроса для выхода пользователя.
    """
    refresh_token: str = Field(..., description="Refresh токен пользователя для выхода")


class SendVerifyCodeRequest(BaseModel):
    """
    Схема запроса для отправки кода верификации email.
    """
    email: EmailStr = Field(..., description="Email для верификации")


class SendResetPasswordCodeRequest(BaseModel):
    """
    Схема запроса для отправки кода сброса пароля.
    """
    email: EmailStr = Field(..., description="Email для сброса пароля")


class VerifyEmailRequest(BaseModel):
    """
    Схема запроса для подтверждения email.
    """
    token: str = Field(..., description="Токен верификации email")


class ResetPasswordRequest(PasswordMixinSchema):
    """
    Схема запроса для сброса пароля.
    """
    token: str = Field(..., description="Токен сброса пароля")


class CallbackRequest(BaseModel):
    code: str
    state: str