
from typing import Literal

from pydantic import BaseModel, Field

from app.core.api.schemas import FilterParam, ListParams, SortParam


class PermissionDTO(BaseModel):
    id: int
    name: str

class PermissionSortParam(SortParam):
    field: Literal["id", "name"]


class PermissionFilterParam(FilterParam):
    field: Literal["name"]


class PermissionListParams(ListParams):
    sort: list[PermissionSortParam] | None = Field(None)
    filters: list[PermissionFilterParam] | None = Field(None)

