from datetime import datetime

from pydantic import BaseModel, Field

from app.auth.filters.sessions import SessionFilter
from app.core.api.filter_mapper import FilterMapper
from app.core.filters.pagination import Pagination


class GetSessionsRequest(BaseModel):
    user_id: int | None = None
    device_id: str | None = None
    last_activity_after: datetime | None = None
    last_activity_before: datetime | None = None
    is_active: bool | None = None

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    sort: str | None = Field(default=None, examples=["created_at:desc,username:asc"])


    def to_session_filter(self) -> SessionFilter:
        session_filter = SessionFilter(
            user_id=self.user_id,
            device_id=self.device_id,
            last_activity_after=self.last_activity_after,
            last_activity_before=self.last_activity_before,
            is_active=self.is_active
        )

        pagination = Pagination(page=self.page, page_size=self.page_size)
        session_filter.set_pagination(pagination)

        sort_fields = FilterMapper.parse_sort_string(self.sort)
        for sort_field in sort_fields:
            session_filter.add_sort(sort_field.field, sort_field.direction)

        return session_filter
