from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeletePermissionToUserCommand(BaseCommand):
    user_jwt_data: UserJWTData
    user_id: int
    permissions: set[str]


@dataclass(frozen=True)
class DeletePermissionToUserCommandHandler(BaseCommandHandler[DeletePermissionToUserCommand, None]):
    session: AsyncSession
    user_repository: UserRepository
    permission_repository: PermissionRepository
    rbac_manager: RBACManager
    token_blacklist: TokenBlacklistRepository

    async def handle(self, command: DeletePermissionToUserCommand) -> None:
        if not self.rbac_manager.check_permission(command.user_jwt_data, {"permission:update", "user:update"}):
            raise

        user = await self.user_repository.get_user_with_permission_by_id(command.user_id)
        if user is None:
            raise

        permissions = await self.permission_repository.get_permissions_by_names(
            command.permissions
        )

        if len(permissions) != len(command.permissions):
            found_names = {p.name for p in permissions}
            missing = command.permissions - found_names
            raise 

        for permission in permissions:
            user.delete_permission(permission)

        await self.token_blacklist.add_user(user.id)
        await self.session.commit()

        logger.info("Delete permission to user", extra={
            "deleted_to": command.user_id,
            "deleted_by": command.user_jwt_data.id,
            "permission": command.permissions
        })
