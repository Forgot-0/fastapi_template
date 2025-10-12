from dataclasses import dataclass

from app.auth.models.permission import Permission
from app.auth.models.role import Role
from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData




@dataclass
class RBACManager:
    user_repository: UserRepository
    role_repository: RoleRepository
    permission_repository: PermissionRepository
    role_invalidation: RoleInvalidateRepository

    # async def create_role(
    #         self, name: str, description: str,
    #         security_level: int, permissions: list[str] | None = None
    #     ) -> Role:

    #     self._validate_role_name(name)

    #     role = Role(
    #         name=name,
    #         description=description,
    #         security_level=security_level,
    #         permissions={
    #             Permission(name=permission) for permission in permissions
    #          } if permissions else set()
    #     )
    #     await self.role_repository.create(role)

    #     return role

    # def _validate_role_name(
    #     self, role_name: str
    # ) -> None:
    #     if len(role_name) > 24 or len(role_name) < 3:
    #         raise 

    #     if role_name.startswith(("system_", "admin_")):
    #         raise 


    async def check_permission(self, jwt_data: UserJWTData, permissions: set[str]) -> bool:
        set_user_permission = set(jwt_data.permissions)

        if not set_user_permission <= permissions:
            return False

        return True