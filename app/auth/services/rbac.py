from collections.abc import Iterable
from dataclasses import dataclass, field

from app.auth.dtos.user import AuthUserJWTData
from app.auth.exceptions import (
    InvalidRoleNameError,
    ProtectedPermissionError,
)
from app.auth.models.role_permission import PermissionEnum, RolesEnum
from app.core.services.auth.exceptions import AccessDeniedError
from app.core.services.auth.rbac import RBACManagerInterface


@dataclass
class AuthRBACManager(RBACManagerInterface):
    system_roles: set[str] = field(init=False)
    protected_permissions: set[str] = field(init=False)

    ROLE_NAME_MIN_LEN: int = field(init=False, default=3)
    ROLE_NAME_MAX_LEN: int = field(init=False, default=24)
    SYSTEM_PREFIXES: tuple = field(init=False, default=("system_", "admin_"))

    def __post_init__(self) -> None:
        self.system_roles = set(
            {
                RolesEnum.SYSTEM_ADMIN.value.name,
                RolesEnum.SUPER_ADMIN.value.name,
            }
        )

        self.protected_permissions = set(
            {
                PermissionEnum.MANAGE_SYSTEM_SETTINGS.value.name,
                PermissionEnum.CREATE_ROLE.value.name,
                PermissionEnum.UPDATE_ROLE.value.name,
                PermissionEnum.ASSIGN_ROLE.value.name,
                PermissionEnum.REMOVE_ROLE.value.name,
                PermissionEnum.CREATE_PERMISSION.value.name,
                PermissionEnum.UPDATE_PERMISSION.value.name,
                PermissionEnum.DELETE_PERMISSION.value.name,
                PermissionEnum.IMPERSONATE_USER.value.name,
            }
        )

    @staticmethod
    def _to_set(iterable: Iterable[str] | None) -> set[str]:
        return set(iterable or ())

    def validate_role_name(self, jwt_data: AuthUserJWTData, role_name: str) -> None:
        if not (self.ROLE_NAME_MIN_LEN <= len(role_name) <= self.ROLE_NAME_MAX_LEN):
            raise InvalidRoleNameError(name=role_name)

        if role_name.startswith(self.SYSTEM_PREFIXES) and not self.is_system_user(jwt_data):
            missing = {"role:create"} - self._to_set(jwt_data.permissions)
            raise AccessDeniedError(need_permissions=missing)

    def validate_permissions(self, jwt_data: AuthUserJWTData, permission_name: str) -> None:
        if self.is_system_user(jwt_data):
            return

        if permission_name in self.protected_permissions:
            raise ProtectedPermissionError(name=permission_name)

        if permission_name not in self._to_set(jwt_data.permissions):
            missing = {permission_name} - self._to_set(jwt_data.permissions)
            raise AccessDeniedError(need_permissions=missing)

    def is_system_user(self, jwt_data: AuthUserJWTData) -> bool:
        return bool(self.system_roles & self._to_set(jwt_data.roles))

    def check_security_level(self, user_level: int, role_level: int) -> None:
        if role_level == 0:
            raise AccessDeniedError(need_permissions=set())

        if user_level <= role_level:
            raise AccessDeniedError(need_permissions=set())

    def check_permission(self, jwt_data: AuthUserJWTData, required_permissions: set[str]) -> bool:

        if not required_permissions:
            return True

        if self.is_system_user(jwt_data):
            return True

        user_perms = self._to_set(jwt_data.permissions)
        return user_perms >= set(required_permissions)
