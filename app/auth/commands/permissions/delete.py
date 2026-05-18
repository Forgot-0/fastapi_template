import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dtos.user import AuthUserJWTData
from app.auth.exceptions import NotFoundPermissionsException, ProtectedPermissionException
from app.auth.repositories.permission import PermissionInvalidateRepository, PermissionRepository
from app.auth.services.rbac import AuthRBACManager
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.services.auth.exceptions import AccessDeniedException

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeletePermissionCommand(BaseCommand):
    name: str
    user_jwt_data: AuthUserJWTData


@dataclass(frozen=True)
class DeletePermissionCommandHandler(BaseCommandHandler[DeletePermissionCommand, None]):
    session: AsyncSession
    permission_repository: PermissionRepository
    rbac_manager: AuthRBACManager
    permission_blacklist: PermissionInvalidateRepository

    async def handle(self, command: DeletePermissionCommand) -> None:
        if not self.rbac_manager.check_permission(command.user_jwt_data, {"permission:create"}):
            raise AccessDeniedException(
                need_permissions={"permission:create"} - set(command.user_jwt_data.permissions)
            )

        self.rbac_manager.validate_permissions(command.user_jwt_data, command.name)

        if command.name in self.rbac_manager.protected_permissions:
            raise ProtectedPermissionException(name=command.name)

        permission = await self.permission_repository.get_permission_by_name(command.name)
        if permission is None:
            raise NotFoundPermissionsException(missing={command.name })

        await self.permission_repository.delete(permission)
        await self.permission_blacklist.invalidate_permission(permission.name)
        await self.session.commit()

        logger.info("Delete permission", extra={
            "deleted_by": command.user_jwt_data.id,
            "permission_name": command.name
        })
