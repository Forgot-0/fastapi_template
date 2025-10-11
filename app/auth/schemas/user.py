from typing import Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.models.user import User
from app.auth.schemas.base import PasswordMixinSchema
from app.auth.schemas.token import AccessToken
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
    security_level: int | None = Field(default=None)
    device_id: str | None = Field(default=None)

    @classmethod
    def create_from_user(cls, user: User, device_id: str | None=None) -> 'UserJWTData':
        if user.jwt_data is None:
            raise

        jwt_data: dict[str, Any] = orjson.loads(user.jwt_data)

        return cls(
            id=str(jwt_data["sub"]),
            security_level=jwt_data['lvl'],
            device_id=device_id,
            roles=jwt_data["roles"],
            permissions=jwt_data["permissions"],
        )

    @classmethod
    def create_from_token(cls, token_dto: AccessToken) -> 'UserJWTData':
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


