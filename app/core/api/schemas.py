import logging
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import UUID

import orjson
from fastapi.responses import ORJSONResponse as _ORJSONResponse
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortParam(BaseModel):
    field: str
    order: SortOrder = SortOrder.ASC


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


T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[T]
    pagination: Pagination


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: dict[str, Any] | list | None = None


ER = TypeVar("ER", bound=ErrorDetail)


class ErrorResponse(BaseModel, Generic[ER]):
    error: ER
    status: int
    request_id: str
    timestamp: float


def additionally_serialize(obj: Any) -> Any:
    match obj:
        case Exception():
            text = obj.args[0] if len(obj.args) > 0 else "Unknown error"
            return f"{obj.__class__.__name__}: {text}"
        case UUID():
            return str(obj)
        case BaseModel():
            return obj.model_dump()

    logger.warning("Type is not JSON serializable: %s", type(obj), extra={"obj": repr(obj)})
    return repr(obj)


class ORJSONResponse(_ORJSONResponse):
    def render(self, content: Any) -> bytes:
        return orjson.dumps(
            content,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
            default=additionally_serialize,
        )
