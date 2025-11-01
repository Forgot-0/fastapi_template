from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import NotFoundPermissionException, NotFoundRoleException
from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeletePermissionRoleCommand(BaseCommand):
    role_name: str
    permissions: set[str]
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class DeletePermissionRoleCommandHandler(BaseCommandHandler[DeletePermissionRoleCommand, None]):
    session: AsyncSession
    role_repository: RoleRepository
    permission_repository: PermissionRepository
    rbac_manager: RBACManager
    role_invalidation: RoleInvalidateRepository

    async def handle(self, command: DeletePermissionRoleCommand) -> None:
        self.rbac_manager.check_permission(command.user_jwt_data, {"role:update", })
        role = await self.role_repository.get_with_permission_by_name(command.role_name)
        if role is None:
            raise NotFoundRoleException(command.role_name)

        for name in command.permissions:
            permission = await self.permission_repository.get_permission_by_name(name)
            if permission is None:
                raise NotFoundPermissionException(name)

            role.delete_permission(permission)

        await self.role_invalidation.invalidate_role(role.name)
        await self.session.commit()
        logging.info("Delete permission to user", extra={
            "role_name": command.role_name,
            "permission": role.permissions,
            "delete_permission_by": command.user_jwt_data.id
        })