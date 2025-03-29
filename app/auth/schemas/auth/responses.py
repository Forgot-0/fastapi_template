from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """
    Схема ответа для аутентификации, содержащая access и refresh токены.
    """
    access_token: str = Field(..., description="Access токен для доступа к защищённым ресурсам")
    refresh_token: str = Field(..., description="Refresh токен для обновления access токена")
    token_type: str = Field(default="bearer", description="Тип токена")


class AccessTokenResponse(BaseModel):
    """
    Схема ответа для обновления access токена.
    """
    access_token: str = Field(..., description="Новый access токен")
