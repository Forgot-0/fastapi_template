from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.core.api.schemas import FilterParam, ListParams, SortParam



class SessionDTO(BaseModel):
    id: int
    user_id: int
    device_info: str
    user_agent: str
    last_activity: datetime
    is_active: bool


class SessionSortParam(SortParam):
    field: Literal['id', 'last_activity', 'created_at']


class SessionFilterParam(FilterParam):
    field: Literal['id', 'user_id', 'device_id', 'is_active']


class SessionListParams(ListParams):
    sort: list[SessionSortParam] | None = Field(None)
    filters: list[SessionFilterParam] | None = Field(None)


