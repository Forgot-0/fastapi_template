from typing import Any, Union

from pydantic import ConfigDict, create_model

from app.core.api.schemas import (
    ErrorDetail,
    ErrorResponse,
)
from app.core.exceptions import ApplicationException


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
