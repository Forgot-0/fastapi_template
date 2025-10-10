from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.session import SessionRepository
from app.auth.security import verify_token
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class LogoutCommand(BaseCommand):
    refresh_token: str


@dataclass(frozen=True)
class LogoutCommandHandler(BaseCommandHandler[LogoutCommand, None]):
    session: AsyncSession
    token_repository: SessionRepository

    async def handle(self, command: LogoutCommand) -> None:
        payload = verify_token(command.refresh_token, token_type='refresh')
        await self.token_repository.revoke_user_device(
            user_id=int(payload.sub), jti=payload.jti
        )
        await self.session.commit()
        logger.info("Logout user", extra={"sub": payload.sub, "device_id": payload.device_id})