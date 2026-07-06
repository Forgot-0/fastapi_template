from dataclasses import dataclass
from typing import Any

from app.core.exceptions import ApplicationError


@dataclass(kw_only=True)
class NotFoundUserError(ApplicationError):
    user_by: str | int
    user_field: str

    code: str = "NOT_FOUND_USER"
    status: int = 404

    @property
    def message(self) -> str:
        return "User not found"

    @property
    def detail(self) -> dict[str, Any]:
        return {"user_by": self.user_by, "user_field": self.user_field}


@dataclass(kw_only=True)
class WrongLoginDataError(ApplicationError):
    username: str

    code: str = "WRONG_LOGIN_DATA"
    status: int = 400

    @property
    def message(self) -> str:
        return "Wrong login data"

    @property
    def detail(self) -> dict[str, Any]:
        return {"username": self.username}


@dataclass(kw_only=True)
class OAuthStateNotFoundError(ApplicationError):
    state: str

    code: str = "OAUTH_STATE_NOT_FOUND"
    status: int = 404

    @property
    def message(self) -> str:
        return "This state not found"

    @property
    def detail(self) -> dict[str, Any]:
        return {"state": self.state}


@dataclass(kw_only=True)
class LinkedAnotherUserOAuthError(ApplicationError):
    provider: str

    code: str = "LINKED_ANOTHER_USER_OAUTH"
    status: int = 409

    @property
    def message(self) -> str:
        return "This provider was linked to another user"

    @property
    def detail(self) -> dict[str, Any]:
        return {"provider": self.provider}


@dataclass(kw_only=True)
class NotFoundRoleError(ApplicationError):
    name: str

    code: str = "NOT_FOUND_ROLE"
    status: int = 404

    @property
    def message(self) -> str:
        return "Role not found"

    @property
    def detail(self) -> dict[str, Any]:
        return {"name": self.name}


@dataclass(kw_only=True)
class InvalidRoleNameError(ApplicationError):
    name: str

    code: str = "INVALID_ROLE_NAME"
    status: int = 400

    @property
    def message(self) -> str:
        return "Invalid role name"

    @property
    def detail(self) -> dict[str, Any]:
        return {"name": self.name}


@dataclass
class NotFoundOrInactiveSessionError(ApplicationError):
    code: str = "NOT_FOUND_OR_INACTIVE_SESSION"
    status: int = 400

    @property
    def message(self) -> str:
        return "Session not found or inactive"

    @property
    def detail(self) -> dict[str, Any]:
        return {}


@dataclass(kw_only=True)
class NotFoundPermissionsError(ApplicationError):
    missing: set[str]

    code: str = "NOT_FOUND_PERMISSIONS"
    status: int = 404

    @property
    def message(self) -> str:
        return "Permissions not found"

    @property
    def detail(self) -> dict[str, Any]:
        return {"permissions": list(self.missing)}


@dataclass(kw_only=True)
class ProtectedPermissionError(ApplicationError):
    name: str

    code: str = "PROTECTED_PERMISSION"
    status: int = 409

    @property
    def message(self) -> str:
        return "Permission is protected and cannot be modified"

    @property
    def detail(self) -> dict[str, Any]:
        return {"permission": self.name}


@dataclass(kw_only=True)
class DuplicateUserError(ApplicationError):
    field: str
    value: str

    code: str = "DUPLICATE_USER"
    status: int = 409

    @property
    def message(self) -> str:
        return "User already exists"

    @property
    def detail(self) -> dict[str, Any]:
        return {"field": self.field, "value": self.value}


@dataclass(kw_only=True)
class DuplicateRoleError(ApplicationError):
    name: str

    code: str = "DUPLICATE_ROLE"
    status: int = 409

    @property
    def message(self) -> str:
        return "Role already exists"

    @property
    def detail(self) -> dict[str, Any]:
        return {"name": self.name}

@dataclass(kw_only=True)
class DuplicatePermissionError(ApplicationError):
    name: str

    code: str = "DUPLICATE_PERMISSION"
    status: int = 409

    @property
    def message(self) -> str:
        return "Permission already exists"

    @property
    def detail(self) -> dict[str, Any]:
        return {"name": self.name}


@dataclass(kw_only=True)
class PasswordMismatchError(ApplicationError):
    code: str = "PASSWORD_MISMATCH"
    status: int = 400

    @property
    def message(self) -> str:
        return "Passwords do not match"

    @property
    def detail(self) -> dict[str, Any]:
        return {}


@dataclass(kw_only=True)
class EmailNotConfirmedError(ApplicationError):
    email: str

    code: str = "EMAIL_NOT_CONFIRMED"
    status: int = 403

    @property
    def message(self) -> str:
        return "Email not confirmed"

    @property
    def detail(self) -> dict[str, Any]:
        return {"email": self.email}


@dataclass(kw_only=True)
class NotExistProviderOAuthError(ApplicationError):
    provider: str

    code: str = "NOT_EXIST_PROVIDER_OAUTH"
    status: int = 400

    @property
    def message(self) -> str:
        return "NOT_EXIST_PROVIDER_OAUTH"

    @property
    def detail(self) -> dict[str, Any]:
        return {"provider": self.provider}


@dataclass
class TokenInBlacklistError(ApplicationError):
    code: str = "TOKEN_IN_BLACKLIST"
    status: int = 409

    @property
    def message(self) -> str:
        return ""
