from datetime import datetime

from pydantic import BaseModel, Field

from app.auth.dtos.user import BaseUser
from app.auth.filters.users import UserFilter
from app.auth.schemas.base import PasswordMixinSchema
from app.core.api.filter_mapper import FilterMapper
from app.core.filters.pagination import Pagination
from app.core.filters.sort import SortDirection


class UserCreateRequest(BaseUser, PasswordMixinSchema):
    ...

class UserPermissionRequest(BaseModel):
    permissions: set[str] = Field(default_factory=set)


class GetUsersRequest(BaseModel):
    email: str | None = None
    username: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    is_deleted: bool | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    has_oauth_accounts: bool | None = None
    has_sessions: bool | None = None
    role_names: list[str] | None = None
    permission_names: list[str] | None = None

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    sort: str | None = Field(default=None, examples=["created_at:desc,username:asc"])


    def to_user_filter(self) -> UserFilter:
        user_filter = UserFilter(
            email=self.email,
            username=self.username,
            is_active=self.is_active,
            is_verified=self.is_verified,
            is_deleted=self.is_deleted,
            created_after=self.created_after,
            created_before=self.created_before,
            updated_after=self.updated_after,
            updated_before=self.updated_before,
            has_oauth_accounts=self.has_oauth_accounts,
            has_sessions=self.has_sessions,
            role_names=self.role_names,
            permission_names=self.permission_names
        )

        pagination = Pagination(page=self.page, page_size=self.page_size)
        user_filter.set_pagination(pagination)

        sort_fields = FilterMapper.parse_sort_string(self.sort)
        for sort_field in sort_fields:
            user_filter.add_sort(sort_field.field, sort_field.direction)

        if not sort_fields:
            user_filter.add_sort("created_at", SortDirection.DESC)

        return user_filter
