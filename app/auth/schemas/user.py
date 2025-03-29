from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

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


class UserCreate(BaseUser):
    """Schema for user creation request."""
    password_hash: str | None = None


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


