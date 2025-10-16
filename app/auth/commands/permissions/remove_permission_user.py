from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.permission import PermissionRepository
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

    async def handle(self, command: DeletePermissionToUserCommand) -> None:
        if not self.rbac_manager.check_permission(command.user_jwt_data, {"permission:update", "user:update"}):
            raise

        user = await self.user_repository.get_user_with_permission_by_id(command.user_id)
        if user is None:
            raise

        for permission in command.permissions:

            permission = await self.permission_repository.get_permission_by_name(permission)
            if permission is None:
                raise

            user.delete_permission(permission)

        await self.session.commit()

        logger.info("Delete permission to user", extra={
            "deleted_to": command.user_id,
            "deleted_by": command.user_jwt_data.id,
            "permission": command.permissions
        })
