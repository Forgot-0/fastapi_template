from dataclasses import dataclass
from typing import Any

from app.core.exceptions import ApplicationError


@dataclass(kw_only=True)
class InvalidTokenError(ApplicationError):
    token: str | None = None

    code: str = "INVALID_TOKEN"
    status: int = 403

    @property
    def message(self) -> str:
        return "Invalid token"

    @property
    def detail(self) -> dict[str, Any]:
        return {}


@dataclass(kw_only=True)
class ExpiredTokenError(ApplicationError):
    token: str | None = None

    code: str = "EXPIRED_TOKEN"
    status: int = 400

    @property
    def message(self) -> str:
        return "Token has expired"

    @property
    def detail(self) -> dict[str, Any]:
        return {}

@dataclass
class NotAuthenticatedError(ApplicationError):
    code: str = "NOT_AUTHNTICATED"
    status: int = 401

    @property
    def message(self) -> str:
        return "Not authenticated"

    @property
    def detail(self) -> dict[str, Any]:
        return {}


@dataclass(kw_only=True)
class AccessDeniedError(ApplicationError):
    need_permissions: set[str]

    code: str = "ACCESS_DENIED"
    status: int = 403

    @property
    def message(self) -> str:
        return "Access denied"

    @property
    def detail(self) -> dict[str, Any]:
        return {"permissions": list(self.need_permissions)}

