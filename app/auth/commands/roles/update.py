import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import AccessDeniedException, NotFoundRoleException
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.commands import BaseCommand, BaseCommandHandler

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class RoleUpdateCommand(BaseCommand):
    id: int
    name: str | None
    description: str | None
    security_level: int | None
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class RoleUpdateCommandHandler(BaseCommandHandler[RoleUpdateCommand, None]):
    session: AsyncSession
    role_repository: RoleRepository
    rbac_manager: RBACManager
    role_invalidation: RoleInvalidateRepository

    async def handle(self, command: RoleUpdateCommand) -> None:
        if not self.rbac_manager.check_permission(command.user_jwt_data, {"role:update" }):
            raise AccessDeniedException(
                need_permissions={"role:update" } - set(command.user_jwt_data.permissions)
            )
        if command.security_level is not None:
            self.rbac_manager.check_security_level(command.user_jwt_data.security_level, command.security_level)

        role = await self.role_repository.get_by_id(command.id)
        if role is None:
            raise NotFoundRoleException(name=str(command.id))

        self.rbac_manager.check_security_level(command.user_jwt_data.security_level, role.security_level)
        role.update({
            "name": command.name, "description": command.description, "security_level": command.security_level
        })

        await self.role_invalidation.invalidate_role(role.name)
        await self.session.commit()

        logger.info("Update role", extra={
            "updated_by": command.user_jwt_data.id,
            "role_id": command.id,
            "role_name": command.name,
            "description": command.description,
            "security_level": command.security_level,
        })
