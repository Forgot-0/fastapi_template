from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RemoveRoleCommand(BaseCommand):
    remove_from_user: int
    role_name: str
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class RemoveRoleCommandHandler(BaseCommandHandler[RemoveRoleCommand, None]):
    session: AsyncSession
    user_repository: UserRepository
    role_repository: RoleRepository
    permission_repository: PermissionRepository
    rbac_manager: RBACManager

    async def handle(self, command: RemoveRoleCommand) -> None:
        self.rbac_manager.check_permission(command.user_jwt_data, {"user:update", "role:remove"})

        role = await self.role_repository.get_with_permission_by_name(command.role_name)
        if role is None:
            raise

        self.rbac_manager.check_security_level(command.user_jwt_data.security_level, role.security_level)

        user = await self.user_repository.get_user_with_permission_by_id(command.remove_from_user)
        if user is None:
            raise

        user.delete_role(role)

        await self.session.commit()
        logger.info("Remove role user", extra={
            "remove_role": command.role_name,
            "remove_to": command.remove_from_user,
            "removed_by": command.user_jwt_data.id,
        })