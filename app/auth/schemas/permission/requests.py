from pydantic import BaseModel, Field

from app.auth.filters.permissions import PermissionFilter
from app.core.api.filter_mapper import FilterMapper
from app.core.filters.pagination import Pagination


class PermissionCreateRequest(BaseModel):
    name: str


class GetPermissionsRequest(BaseModel):
    name: str | None = None

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    sort: str | None = Field(default=None, examples=["created_at:desc,username:asc"])


    def to_permission_filter(self) -> PermissionFilter:
        role_filter = PermissionFilter(
            name=self.name,
        )

        pagination = Pagination(page=self.page, page_size=self.page_size)
        role_filter.set_pagination(pagination)

        sort_fields = FilterMapper.parse_sort_string(self.sort)
        for sort_field in sort_fields:
            role_filter.add_sort(sort_field.field, sort_field.direction)

        return role_filter
