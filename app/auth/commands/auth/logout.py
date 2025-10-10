from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.session import SessionRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.jwt import JWTManager
from app.auth.services.session import SessionManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class LogoutCommand(BaseCommand):
    refresh_token: str | None


@dataclass(frozen=True)
class LogoutCommandHandler(BaseCommandHandler[LogoutCommand, None]):
    session: AsyncSession
    session_manager: SessionManager
    jwt_manager: JWTManager
    session_repository: SessionRepository


    async def handle(self, command: LogoutCommand) -> None:
        if command.refresh_token is None:
            raise

        refresh_data = await self.jwt_manager.validate_token(command.refresh_token)
        await self.jwt_manager.revoke_token(command.refresh_token)
        user = UserJWTData.create_from_token(refresh_data)

        await self.session_repository.deactivate_user_session(
            user_id=int(user.id),
            device_id=user.device_id,
        )

        await self.session.commit()
        logger.info("Logout user", extra={"sub": user.id, "device_id": user.device_id})