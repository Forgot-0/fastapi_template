from typing import Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.models.user import User
from app.auth.schemas.base import PasswordMixinSchema
from app.auth.schemas.token import Token
from app.core.api.schemas import FilterParam, ListParams, SortParam


class BaseUser(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
    username: str = Field(
        min_length=4,
        max_length=100,
        pattern=r"^[a-zA-Z0-9 ,.\'-]+$",
        description="Позывной может содержать буквы, цифры, пробелы, а также '-' и '_'.",
    )
    email: EmailStr

class UserJWTData(BaseModel):
    id: str
    roles: list[str]
    permissions: list[str]
    security_level: int
    device_id: str | None = Field(default=None)

    @classmethod
    def create_from_user(cls, user: User, device_id: str | None=None) -> 'UserJWTData':
        security_lvl = 0
        permissions = set()
        roles = set()

        for role in user.roles:
            roles.add(role.name)

            security_lvl = max(security_lvl, role.security_level)

            for permission in role.permissions:
                permissions.add(permission.name)

        return cls(
            id=str(user.id),
            security_level=security_lvl,
            roles=list(roles),
            permissions=list(permissions),
            device_id=device_id
        )

    @classmethod
    def create_from_token(cls, token_dto: Token) -> 'UserJWTData':
        return cls(
            id=token_dto.sub,
            roles=token_dto.roles,
            permissions=token_dto.permissions,
            device_id=token_dto.did,
            security_level=token_dto.lvl,
        )


class UserCreate(BaseUser, PasswordMixinSchema):
    """Schema for user creation request."""
    ...


class UserDTO(BaseUser):
    id: int
    is_active: bool
    is_verified: bool


class UserSortParam(SortParam):
    field: Literal['id', 'username', 'created_at']


class UserFilterParam(FilterParam):
    field: Literal['id', 'username']


class UserListParams(ListParams):
    sort: list[UserSortParam] | None = Field(None)
    filters: list[UserFilterParam] | None = Field(None)


