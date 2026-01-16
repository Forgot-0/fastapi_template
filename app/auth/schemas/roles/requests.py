from pydantic import BaseModel, Field

from app.auth.filters.roles import RoleFilter
from app.core.api.filter_mapper import FilterMapper
from app.core.filters.pagination import Pagination


class RoleCreateRequest(BaseModel):
    name: str
    description: str
    security_level: int
    permissions: set[str] = Field(default_factory=set)


class RoleAssignRequest(BaseModel):
    role_name: str


class RoleRemoveRequest(BaseModel):
    role_name: str


class RolePermissionRequest(BaseModel):
    permission: set[str] = Field(default_factory=set)


class GetRolesRequest(BaseModel):
    name: str | None = None
    security_level: int | None = None
    min_security_level: int | None = None
    max_security_level: int | None = None
    permission_names: list[str] | None = None

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    sort: str | None = Field(default=None, examples=["created_at:desc,username:asc"])


    def to_role_filter(self) -> RoleFilter:
        role_filter = RoleFilter(
            name=self.name,
            security_level=self.security_level,
            min_security_level=self.min_security_level,
            max_security_level=self.max_security_level,
            permission_names=self.permission_names
        )

        pagination = Pagination(page=self.page, page_size=self.page_size)
        role_filter.set_pagination(pagination)

        sort_fields = FilterMapper.parse_sort_string(self.sort)
        for sort_field in sort_fields:
            role_filter.add_sort(sort_field.field, sort_field.direction)

        return role_filter
