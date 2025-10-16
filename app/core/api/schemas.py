from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.core.exceptions import ApplicationException



class SortOrder(str, Enum):
    asc = 'asc'
    desc = 'desc'


class SortParam(BaseModel):
    field: str
    order: SortOrder = SortOrder.asc


class FilterParam(BaseModel):
    field: str
    value: int | str | list


class ListParams(BaseModel):
    sort: list[SortParam] | None = Field(None)
    filters: list[FilterParam] | None = Field(None)
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1)

class ListParamsWithoutPagination(BaseModel):
    sort: list[SortParam] | None = Field(None)
    filters: list[FilterParam] | None = Field(None)

class Pagination(BaseModel):
    total: int
    page: int
    page_size: int


T = TypeVar('T')


class PaginatedResult(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[T]
    pagination: Pagination

