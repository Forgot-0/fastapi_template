from enum import Enum

from app.auth.models.permission import Permission
from app.auth.models.role import Role



class PermissionEnum(Enum):
    # System Management
    MANAGE_SYSTEM_SETTINGS = Permission(name="system:manage_settings")
    VIEW_SYSTEM_LOGS = Permission(name="system:view_logs")

    # User Management
    CREATE_USER = Permission(name="user:create")
    UPDATE_USER = Permission(name="user:update")
    DELETE_USER = Permission(name="user:delete")
    VIEW_USER = Permission(name="user:view")
    IMPERSONATE_USER = Permission(name="user:impersonate")

    # Role Management
    CREATE_ROLE = Permission(name="role:create")
    UPDATE_ROLE = Permission(name="role:update")
    DELETE_ROLE = Permission(name="role:delete")
    VIEW_ROLE = Permission(name="role:view")
    ASSIGN_ROLE = Permission(name="role:assign")
    REMOVE_ROLE = Permission(name="role:remove")

    # Permission Management
    CREATE_PERMISSION = Permission(name="permission:create")
    UPDATE_PERMISSION = Permission(name="permission:update")
    DELETE_PERMISSION = Permission(name="permission:delete")
    VIEW_PERMISSION = Permission(name="permission:view")

    @classmethod
    def get_allpermissions(cls) -> set[Permission]:
        return {permission.value for permission in cls}


class RolesEnum(Enum):
    SUPER_ADMIN = Role(
        name="super_admin",
        description="Complete system access with all permissions",
        security_level=10,
        permissions=PermissionEnum.get_allpermissions(),
    )

    SYSTEM_ADMIN = Role(
        name="system_admin",
        description="Manages system settings and organizations",
        security_level=9,
        permissions={
            PermissionEnum.MANAGE_SYSTEM_SETTINGS.value,
            PermissionEnum.VIEW_SYSTEM_LOGS.value,
            PermissionEnum.CREATE_USER.value,
            PermissionEnum.UPDATE_USER.value,
            PermissionEnum.DELETE_USER.value,
            PermissionEnum.VIEW_USER.value,
            PermissionEnum.VIEW_ROLE.value,
            PermissionEnum.ASSIGN_ROLE.value,
            PermissionEnum.REMOVE_ROLE.value,
        },
    )

    STANDARD_USER = Role(
        name="user",
        description="Normal application access",
        security_level=1,
        permissions=set()
    )

    @classmethod
    def get_all_roles(cls) -> list[Role]:
        return [role.value for role in cls]
