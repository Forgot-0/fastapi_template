from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.role import RoleRepository
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

    async def handle(self, command: RoleUpdateCommand) -> None:
        self.rbac_manager.check_permission(command.user_jwt_data, {"role:update", })
        if command.security_level is not None:
            self.rbac_manager.check_security_level(command.user_jwt_data.security_level, command.security_level)

        role = await self.role_repository.get_by_id(command.id)
        if role is None:
            raise

        self.rbac_manager.check_security_level(command.user_jwt_data.security_level, role.security_level)
        role.update(name=command.name, description=command.name, security_level=command.security_level)
        await self.session.commit()

        logger.info("Update role", extra={
            "updated_by": command.user_jwt_data.id,
            "role_id": command.id,
            "name": command.name,
            "description": command.description,
            "security_level": command.security_level,
        })
