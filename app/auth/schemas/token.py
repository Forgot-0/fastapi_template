from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class AccessTokenPayload(BaseModel):
    sub: str
    exp: datetime

class RefreshTokenCreate(BaseModel):
    user_id: int
    expires_at: datetime
    jti: str
    device_id: str

class TokenPayload(BaseModel):
    sub: str
    jti: str
    exp: datetime
    device_id: str
    type: Literal['access', 'refresh']

class ResetToken(BaseModel):
    sub: str
    exp: datetime

class TokenGroup(BaseModel):
    refresh_token: str
    access_token: str

class VerifyToken(BaseModel):
    sub: str
    exp: datetime