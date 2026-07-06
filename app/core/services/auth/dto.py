from enum import Enum
from typing import Self

from pydantic import BaseModel, Field


class JwtTokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class Token(BaseModel):
    type: str
    sub: str
    lvl: int
    jti: str
    did: str
    exp: float
    iat: float
    username: str
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class UserJWTData(BaseModel):
    id: str
    username: str
    roles: list[str]
    permissions: list[str]
    security_level: int
    device_id: str | None = Field(default=None)

    @classmethod
    def create_from_token(cls, token_dto: Token) -> Self:
        return cls(
            id=token_dto.sub,
            username=token_dto.username,
            roles=token_dto.roles,
            permissions=token_dto.permissions,
            device_id=token_dto.did,
            security_level=token_dto.lvl,
        )

    def to_dict(self) -> dict:
        return {
            "sub": self.id,
            "username": self.username,
            "roles": self.roles,
            "permissions": self.permissions,
            "lvl": self.security_level,
            "did": self.device_id,
        }
