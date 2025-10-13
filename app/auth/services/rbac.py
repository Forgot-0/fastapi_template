from dataclasses import dataclass, field

from app.auth.models.permission import Permission
from app.auth.models.role import Role
from app.auth.models.role_permission import PermissionEnum, RolesEnum
from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData




@dataclass
class RBACManager:
    system_roles: set[str] = field(
        default_factory=lambda: {RolesEnum.SYSTEM_ADMIN.value.name, RolesEnum.SUPER_ADMIN.value.name}
    )

    protected_permissions: set[str] = field(default_factory=lambda: {
        PermissionEnum.MANAGE_SYSTEM_SETTINGS.value.name,

        PermissionEnum.CREATE_ROLE.value.name,
        PermissionEnum.UPDATE_ROLE.value.name,
        PermissionEnum.ASSIGN_ROLE.value.name,
        PermissionEnum.REMOVE_ROLE.value.name,

        PermissionEnum.CREATE_PERMISSION.value.name,
        PermissionEnum.UPDATE_PERMISSION.value.name,
        PermissionEnum.DELETE_PERMISSION.value.name,

        PermissionEnum.IMPERSONATE_USER.value.name,
    })

    def validate_role_name(
        self, jwt_data: UserJWTData, role_name: str
    ) -> None:
        if len(role_name) > 24 or len(role_name) < 3:
            raise 

        if role_name.startswith(("system_", "admin_")) and not self.is_system_user(jwt_data):
            raise 

    def validate_permissions(self, jwt_data: UserJWTData, permission_name: str) -> None:
        if self.is_system_user(jwt_data):
            return

        if permission_name in self.protected_permissions:
            raise

        if permission_name not in jwt_data.permissions:
            raise

    def is_system_user(self, jwt_data: UserJWTData) -> bool:
        return any(role in self.system_roles for role in jwt_data.roles)

    def check_security_level(self, user_level: int, role_level: int) -> None:
        if role_level == 0:
            raise 

        if user_level >= role_level:
            raise

    def check_permission(self, jwt_data: UserJWTData, permissions: set[str]) -> bool:
        set_user_permission = set(jwt_data.permissions)

        if self.is_system_user(jwt_data):
            return True

        if not set_user_permission <= permissions:
            return False

        return True
