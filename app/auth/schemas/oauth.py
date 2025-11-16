from dataclasses import dataclass
from pydantic import BaseModel, Field


class OAuthUserInfo(BaseModel):
    provider_user_id: str
    email: str
    name: str | None = None


@dataclass
class OAuthCallbackData:
    provider_user_id: str
    provider_email: str
    name: str | None = None


class OAuthLoginRequest(BaseModel):
    code: str
    provider: str


class OAuthConnectRequest(BaseModel):
    code: str
    provider: str