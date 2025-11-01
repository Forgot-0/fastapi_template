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

        for name in command.permissions:
            self.rbac_manager.validate_permissions(command.user_jwt_data, name)
            permission = await self.permission_repository.get_permission_by_name(name)
            if permission is None:
                raise

            role.add_permission(permission)

        await self.role_invalidation.invalidate_role(role.name)
        await self.session.commit()
        logger.info("Add permission to role", extra={
            "role_name": command.role_name,
            "permission": role.permissions,
            "add_permission_by": command.user_jwt_data.id
        })