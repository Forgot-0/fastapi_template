from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.permission import Permission
from app.auth.models.role import Role
from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class CreateRoleCommand(BaseCommand):
    user_jwt_data: UserJWTData
    role_name: str
    description: str
    security_level: int
    permissions: set[str]


@dataclass(frozen=True)
class CreateRoleCommandHandler(BaseCommandHandler[CreateRoleCommand, None]):
    session: AsyncSession
    role_repository: RoleRepository
    permission_repository: PermissionRepository
    rbac_manager: RBACManager

    async def handle(self, command: CreateRoleCommand) -> None:
        self.rbac_manager.check_permission(command.user_jwt_data, {"role:create", })

        self.rbac_manager.validate_role_name(command.user_jwt_data, command.role_name)
        self.rbac_manager.check_security_level(command.user_jwt_data.security_level, command.security_level)


        role = await self.role_repository.get_by_name(command.role_name)
        if role is not None:
            raise

        role = Role(
            name=command.role_name,
            description=command.description,
            security_level=command.security_level,
        )

        for name in command.permissions:
            permission = await self.permission_repository.get_permission_by_name(name)

            if permission is None:
                raise

            self.rbac_manager.validate_permissions(command.user_jwt_data, name)
            role.add_permission(permission)

        await self.role_repository.create(role)
        await self.session.commit()

        logger.info("Create new role", extra={"role": role.name, "created_by": command.user_jwt_data.id})
