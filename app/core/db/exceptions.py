from dataclasses import dataclass

from app.core.exceptions import ApplicationError


@dataclass(eq=False, kw_only=True)
class AttributeNotExistError(ApplicationError):
    field: str
    code: int = 400
    status: str = "ATTRIBUTE_NOT_EXIST"

    @property
    def message(self) -> str:
        return "This attribute does not exist"

    @property
    def detail(self) -> dict:
        return {
            "attribute": self.field
        }
