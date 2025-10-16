
from typing import Literal
from pydantic import BaseModel, Field

from app.core.api.schemas import FilterParam, ListParams, SortParam



class BaseRole(BaseModel):
    name: str
    description: str
    security_level: int
    permissions: set[str] = Field(default_factory=set)


class RoleDTO(BaseRole):
    id: int


class RoleSortParam(SortParam):
    field: Literal['id', 'security_level']


class RoleFilterParam(FilterParam):
    field: Literal['name', 'description', 'permissions']


class RoleListParams(ListParams):
    sort: list[RoleSortParam] | None = Field(None)
    filters: list[RoleFilterParam] | None = Field(None)

