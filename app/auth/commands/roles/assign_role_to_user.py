from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.auth.exceptions import AccessDeniedException, NotFoundRoleException, NotFoundUserException
from app.core.commands import BaseCommand, BaseCommandHandler



logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AssignRoleCommand(BaseCommand):
    assign_to_user: int
    role_name: str
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class AssignRoleCommandHandler(BaseCommandHandler[AssignRoleCommand, None]):
    session: AsyncSession
    role_repository: RoleRepository
    user_repository: UserRepository
    permission_repository: PermissionRepository
    rbac_manager: RBACManager
    token_blacklist: TokenBlacklistRepository

    async def handle(self, command: AssignRoleCommand) -> None:
        if not self.rbac_manager.check_permission(command.user_jwt_data, {"role:assign", }):
            raise AccessDeniedException(
                need_permissions={"role:assign", } - set(command.user_jwt_data.permissions)
            )
        role = await self.role_repository.get_by_name(command.role_name)
        if role is None:
            raise NotFoundRoleException(name=command.role_name)

        assign_user = await self.user_repository.get_user_with_permission_by_id(command.assign_to_user)
        if assign_user is None:
            raise NotFoundUserException(user_by=command.assign_to_user, user_field="id")

        self.rbac_manager.check_security_level(
            command.user_jwt_data.security_level,
            role.security_level
        )

        assign_user.add_role(role)
        await self.token_blacklist.add_user(assign_user.id)

        await self.session.commit()
        logger.info("Role assigned", extra={
                "role_name": command.role_name,
                "assigned_to": assign_user.id,
                "assigned_by": command.user_jwt_data.id
            }
        )
