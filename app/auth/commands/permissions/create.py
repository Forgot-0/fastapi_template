import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import AccessDeniedException, NotFoundPermissionsException
from app.auth.models.permission import Permission
from app.auth.repositories.permission import PermissionRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.commands import BaseCommand, BaseCommandHandler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreatePermissionCommand(BaseCommand):
    name: str
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class CreatePermissionCommandHandler(BaseCommandHandler[CreatePermissionCommand, None]):
    session: AsyncSession
    permission_repository: PermissionRepository
    rbac_manager: RBACManager

    async def handle(self, command: CreatePermissionCommand) -> None:
        if not self.rbac_manager.check_permission(command.user_jwt_data, {"permission:create"}):
            raise AccessDeniedException(
                need_permissions={"permission:create"} - set(command.user_jwt_data.permissions)
            )

        self.rbac_manager.validate_permissions(command.user_jwt_data, command.name)

        permission = await self.permission_repository.get_permission_by_name(command.name)
        if permission is not None:
            raise NotFoundPermissionsException(missing={command.name })

        permission = Permission(name=command.name)
        await self.permission_repository.create(permission)
        await self.session.commit()
        logger.info("Create permission", extra={
            "created_by": command.user_jwt_data.id,
            "permission_name": command.name
        })
