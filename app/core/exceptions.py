from dataclasses import dataclass
from typing import Any


@dataclass
class ApplicationException(Exception):
    code: str
    status: int

    @property
    def message(self) -> str:
        return ""

    @property
    def detail(self) -> dict[str, Any]:
        return {}


@dataclass(kw_only=True)
class NotHandlerRegisterException(ApplicationException):
    classes: list[str]
    code: str = "INTERNAL_EXCEPTION"
    status: int = 503

    @property
    def message(self):
        return "No handler/handlers registered"

    @property
    def detail(self) :
        return {"classes": self.classes}