from dataclasses import dataclass

from app.core.exceptions import ApplicationException



@dataclass(kw_only=True)
class NotFoundUserException(ApplicationException):
    user_by: str | int
    user_field: str

    code: str = "NOT_FOUND_USER"
    status: int = 404

    @property
    def message(self):
        return "User not found"

    @property
    def detail(self):
        return {"user_by": self.user_by, "user_field": self.user_field}


@dataclass(kw_only=True)
class WrongLoginDataException(ApplicationException):
    username: str

    code: str = "WRONG_LOGIN_DATA"
    status: int = 400

    @property
    def message(self):
        return "Wrong login data"

    @property
    def detail(self):
        return {"username": self.username}


@dataclass(kw_only=True)
class OAuthStateNotFoundException(ApplicationException):
    state: str

    code: str = "OAUTH_STATE_NOT_FOUND"
    status: int = 404

    @property
    def message(self):
        return "This state not found"

    @property
    def detail(self):
        return {"state": self.state}


@dataclass(kw_only=True)
class LinkedAnotherUserOAuthException(ApplicationException):
    provider: str

    code: str = "LINKED_ANOTHER_USER_OAUTH"
    status: int = 409

    @property
    def message(self):
        return "This provider was linked to another user"

    @property
    def detail(self):
        return {"provider": self.provider}


@dataclass(kw_only=True)
class NotFoundRoleException(ApplicationException):
    name: str

    code: str = "NOT_FOUND_ROLE"
    status: int = 404

    @property
    def message(self):
        return "Role not found"

    @property
    def detail(self):
        return {"name": self.name}


@dataclass(kw_only=True)
class InvalidRoleNameException(ApplicationException):
    name: str

    code: str = "INVALID_ROLE_NAME"
    status: int = 400

    @property
    def message(self):
        return "Invalid role name"

    @property
    def detail(self):
        return {"name": self.name}


@dataclass
class NotFoundOrInactiveSessionException(ApplicationException):
    code: str = "NOT_FOUND_OR_INACTIVE_SESSION"
    status: int = 400

    @property
    def message(self):
        return "Session not found or inactive"

    @property
    def detail(self):
        return {}


@dataclass(kw_only=True)
class AccessDeniedException(ApplicationException):
    need_permissions: set[str]

    code: str = "ACCESS_DENIED"
    status: int = 403

    @property
    def message(self):
        return "Access denied"

    @property
    def detail(self):
        return {"permissions": list(self.need_permissions)}


@dataclass(kw_only=True)
class NotFoundPermissionsException(ApplicationException):
    missing: set[str]

    code: str = "NOT_FOUND_PERMISSIONS"
    status: int = 404

    @property
    def message(self):
        return "Permissions not found"

    @property
    def detail(self):
        return {"permissions": list(self.missing)}


@dataclass(kw_only=True)
class ProtectedPermissionException(ApplicationException):
    name: str

    code: str = "PROTECTED_PERMISSION"
    status: int = 409

    @property
    def message(self):
        return "Permission is protected and cannot be modified"

    @property
    def detail(self):
        return {"permission": self.name}


@dataclass(kw_only=True)
class DuplicateUserException(ApplicationException):
    field: str
    value: str

    code: str = "DUPLICATE_USER"
    status: int = 409

    @property
    def message(self):
        return "User already exists"

    @property
    def detail(self):
        return {"field": self.field, "value": self.value}


@dataclass(kw_only=True)
class DuplicateRoleException(ApplicationException):
    name: str

    code: str = "DUPLICATE_ROLE"
    status: int = 409

    @property
    def message(self):
        return "Role already exists"

    @property
    def detail(self):
        return {"name": self.name}


@dataclass(kw_only=True)
class PasswordMismatchException(ApplicationException):
    code: str = "PASSWORD_MISMATCH"
    status: int = 400

    @property
    def message(self):
        return "Passwords do not match"

    @property
    def detail(self):
        return {}


@dataclass(kw_only=True)
class InvalidTokenException(ApplicationException):
    token: str | None = None

    code: str = "INVALID_TOKEN"
    status: int = 400

    @property
    def message(self):
        return "Invalid token"

    @property
    def detail(self):
        return {"token": self.token}


@dataclass(kw_only=True)
class ExpiredTokenException(ApplicationException):
    token: str | None = None

    code: str = "EXPIRED_TOKEN"
    status: int = 400

    @property
    def message(self):
        return "Token has expired"

    @property
    def detail(self):
        return {"token": self.token}


@dataclass(kw_only=True)
class EmailNotConfirmedException(ApplicationException):
    email: str

    code: str = "EMAIL_NOT_CONFIRMED"
    status: int = 403

    @property
    def message(self):
        return "Email not confirmed"

    @property
    def detail(self):
        return {"email": self.email}


@dataclass(kw_only=True)
class NotExistProviderOAuthException(ApplicationException):
    provider: str

    code: str = "NOT_EXIST_PROVIDER_OAUTH"
    status: int = 400

    @property
    def message(self):
        return "NOT_EXIST_PROVIDER_OAUTH"

    @property
    def detail(self):
        return {"provider": self.provider}