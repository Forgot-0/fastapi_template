from dataclasses import dataclass

from app.core.exceptions import ApplicationError


@dataclass(eq=False, kw_only=True)
class PaginationParamsError(ApplicationError):
    field: str
    limit: int
    code: str = "PAGINATION_PARAMS"
    status: int = 400

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
    code: str = "VALUE_MUST_NOT_NONE"
    status: int = 400

    @property
    def message(self) -> str:
        return "The value must not be empty"

    @property
    def detail(self) -> dict:
        return {
            "field": self.field
        }
