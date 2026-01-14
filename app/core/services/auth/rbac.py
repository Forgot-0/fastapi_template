from dataclasses import dataclass, field

from app.core.services.auth.dto import UserJWTData


@dataclass
class RBACManager:
    system_roles: set[str] = field(
        default_factory=lambda: {"system_admin", "super_admin"}
    )

    def is_system_user(self, jwt_data: UserJWTData) -> bool:
        return any(role in self.system_roles for role in jwt_data.roles)

    def check_permission(self, jwt_data: UserJWTData, permissions: set[str]) -> bool:
        set_user_permission = set(jwt_data.permissions)
        if self.is_system_user(jwt_data):
            return True

        return set_user_permission >= permissions
