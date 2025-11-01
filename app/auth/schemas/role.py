
from typing import Literal
from pydantic import BaseModel, Field

from app.auth.schemas.permissions import PermissionDTO
from app.core.api.schemas import FilterParam, ListParams, SortParam



class BaseRole(BaseModel):
    name: str
    description: str
    security_level: int
    permissions: list[PermissionDTO] = Field(default_factory=list)


class RoleDTO(BaseRole):
    id: int


class RoleSortParam(SortParam):
    field: Literal['id', 'security_level']


class RoleFilterParam(FilterParam):
    field: Literal['name', 'description', 'permissions', "security_level"]


class RoleListParams(ListParams):
    sort: list[RoleSortParam] | None = Field(None)
    filters: list[RoleFilterParam] | None = Field(None)

