from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import NotFoundSessionException, PermissionDeniedException
from app.auth.repositories.session import SessionRepository, TokenBlacklistRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UserDeactivateSessionCommand(BaseCommand):
    session_id: int
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class UserDeactivateSessionCommandHandler(BaseCommandHandler[UserDeactivateSessionCommand, None]):
    session: AsyncSession
    session_repository: SessionRepository
    rbac_manager: RBACManager

    async def handle(self, command: UserDeactivateSessionCommand) -> None:
        session = await self.session_repository.get_by_id(command.session_id)
        if not session:
            raise NotFoundSessionException()

        if (
            session.user_id != int(command.user_jwt_data.id) and
            not self.rbac_manager.check_permission(command.user_jwt_data, {"user:update", })
        ): raise PermissionDeniedException()

        session.deactivate()
        await self.session.commit()
        logger.info(
            "Deactivate session",
            extra={
                "deactivated_by": command.user_jwt_data.id,
                "sesion_id": command.session_id
            }
        )