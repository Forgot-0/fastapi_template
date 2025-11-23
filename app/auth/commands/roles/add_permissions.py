from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.commands import BaseCommand, BaseCommandHandler



logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddPermissionRoleCommand(BaseCommand):
    role_name: str
    permissions: set[str]
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class AddPermissionRoleCommandHandler(BaseCommandHandler[AddPermissionRoleCommand, None]):
    session: AsyncSession
    role_repository: RoleRepository
    permission_repository: PermissionRepository
    rbac_manager: RBACManager
    role_invalidation: RoleInvalidateRepository

    async def handle(self, command: AddPermissionRoleCommand) -> None:
        if not self.rbac_manager.check_permission(command.user_jwt_data, {"role:create", }):
            raise 

        role = await self.role_repository.get_with_permission_by_name(command.role_name)
        if role is None:
            raise 

        self.rbac_manager.check_security_level(command.user_jwt_data.security_level, role.security_level)

        permissions = await self.permission_repository.get_permissions_by_names(
            command.permissions
        )

        if len(permissions) != len(command.permissions):
            found_names = {p.name for p in permissions}
            missing = command.permissions - found_names
            raise 

        for permission in permissions:
            role.add_permission(permission)

        await self.role_invalidation.invalidate_role(role.name)
        await self.session.commit()
        logger.info("Add permission to role", extra={
            "role_name": command.role_name,
            "permission": role.permissions,
            "add_permission_by": command.user_jwt_data.id
        })