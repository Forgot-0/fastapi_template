import ast
import re
from dataclasses import dataclass
from typing import Any, Union

from fastapi import Query
from pydantic import ConfigDict, ValidationError, create_model

from app.core.api.schemas import (
    ErrorDetail,
    ErrorResponse,
    FilterParam,
    ListParams,
    ListParamsWithoutPagination,
    SortOrder,
    SortParam,
)
from app.core.exceptions import ApplicationException



@dataclass(frozen=True)
class BuilderFilters:
    filter_param: type[FilterParam]

    def _build_filters(self, value: str | None) -> list[FilterParam] | None:
        if value is None:
            return None

        try:
            items = re.split(r",(?![^\[]*])", value)
            items = [item.strip() for item in items if item.strip()]
        except Exception:
            raise ValidationError("invalid_filter_format")

        return [self._parse_filter_item(item) for item in items]

    def _parse_filter_item(self, item: str) -> FilterParam:
        if ":" not in item:
            raise ValidationError("invalid_filter_field_format")

        field, value = item.split(":", 1)
        return self.filter_param(field=field, value=self._convert_filter_value(value))

    def _convert_filter_value(self, value: str) -> str | int | list:
        if value.startswith("[") and value.endswith("]"):
            try:
                list_value = ast.literal_eval(value)
                if not isinstance(list_value, list):
                    raise ValueError
                return [self._convert_single_value(v) for v in list_value]
            except Exception:
                raise ValidationError("invalid_filter_list_value_format")
        else:
            return self._convert_single_value(value)

    def _convert_single_value(self, value: str) -> str | int:
        try:
            return int(value)
        except ValueError:
            return value


@dataclass(frozen=True)
class BuilderSort:
    sort_param: type[SortParam]

    def _build_sort(self, value: str | None) -> list[SortParam] | None:
        if value is None:
            return None

        try:
            items = [item.strip() for item in value.split(",") if item.strip()]
        except Exception:
            raise ValidationError("invalid_format")

        return [
            self.sort_param(
                field=item.split(":")[0], order=SortOrder(item.split(":")[1]) if ":" in item else SortOrder.ASC
            )
            if isinstance(item, str)
            else item
            for item in items
        ]


@dataclass(frozen=True)
class ListParamsBuilder(BuilderFilters, BuilderSort):
    list_params: type[ListParams]

    def __call__(
        self,
        sort: str | None = Query(None, description="Sort parameters (e.g., field1:asc,field2:desc)"),
        filters: str | None = Query(None, description="Filter parameters (e.g., field1:value1,field2:[value1,value2])"),
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    ) -> ListParams:
        return self.list_params(
            sort=self._build_sort(sort), filters=self._build_filters(filters), page=page, page_size=page_size
        )


@dataclass(frozen=True)
class ListWithoutPaginationParamsBuilder(BuilderFilters, BuilderSort):
    list_params: type[ListParamsWithoutPagination]

    def __call__(
        self,
        sort: str | None = Query(None, description="Sort parameters (e.g., field1:asc,field2:desc)"),
        filters: str | None = Query(None, description="Filter parameters (e.g., field1:value1,field2:[value1,value2])"),
    ) -> ListParamsWithoutPagination:
        return self.list_params(
            sort=self._build_sort(sort), filters=self._build_filters(filters)
        )


def create_response(
    excs: ApplicationException | list[ApplicationException],
    description: str = "",
) -> dict[str, Any]:

    if isinstance(excs, ApplicationException):
        exc_list: list[ApplicationException] = [excs]
    else:
        exc_list = list(excs)

    models: list[type[ErrorDetail]] = []
    examples: dict[str, dict[str, Any]] = {}
    for exc in exc_list:

        model_name = f"ErrorResponse_{exc.__class__.__name__}"

        example_payload: dict[str, Any] = {
            "code": exc.code,
            "message": exc.message,
            "detail": exc.detail,
        }

        error_model = create_model(
            model_name, __base__=ErrorDetail,
            __config__=ConfigDict(json_schema_extra={"example": example_payload})
        )

        models.append(error_model)
        examples[exc.__class__.__name__] = {
            "summary": exc.__class__.__name__,
            "value": {
                "error": example_payload,
                "status": exc.status,
                "request_id": "<uuid>",
                "timestamp": "<timestamp>",
            },
        }

    if len(models) == 1:
        param_model = ErrorResponse[next(iter(models))]
        param_model.model_config = ConfigDict(
            json_schema_extra={"schema_extra": {"example": next(iter(examples.values()))["value"]}}
        )

        content = {
            "application/json": {
                "example": next(iter(examples.values()))["value"],
            }
        }
    else:
        union_type = Union[*models]
        param_model = ErrorResponse[union_type]
        first_example = next(iter(examples.values()))["value"]
        param_model.model_config = ConfigDict(
            json_schema_extra={
                "schema_extra": {
                    "example": first_example, "examples": {k: v["value"] for k, v in examples.items()}
                }
            },
        )
        content = {
            "application/json": {
                "examples": examples,
            }
        }

    return {
        "description": description,
        "model": param_model,
        "content": content,
    }
