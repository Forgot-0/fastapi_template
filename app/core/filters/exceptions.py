from dataclasses import dataclass

from app.core.exceptions import ApplicationError


@dataclass(eq=False, kw_only=True)
class PaginationParamsError(ApplicationError):
    field: str
    limit: int
    code: int = 400
    status: str = "PAGINATION_PARAMS"

    @property
    def message(self) -> str:
        return "Invalida pagination params"

    @property
    def detail(self) -> dict:
        return {
            self.field: self.limit
        }


@dataclass(eq=False, kw_only=True)
class ValueMustNotNoneError(ApplicationError):
    field: str
    code: int = 400
    status: str = "VALUE_MUST_NOT_NONE"

    @property
    def message(self) -> str:
        return "The value must not be empty"

    @property
    def detail(self) -> dict:
        return {
            "field": self.field
        }
