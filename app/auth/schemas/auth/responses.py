from pydantic import BaseModel, Field


class AccessTokenResponse(BaseModel):
    """
    Схема ответа для обновления access токена.
    """
    access_token: str = Field(..., description="Новый access токен")

