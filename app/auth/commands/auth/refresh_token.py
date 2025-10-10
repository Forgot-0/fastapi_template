from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidJWTTokenException
from app.auth.repositories.session import SessionRepository
from app.auth.schemas.token import TokenGroup
from app.auth.security import create_access_token, verify_token
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class RefreshTokenCommand(BaseCommand):
    refresh_token: str


@dataclass(frozen=True)
class RefreshTokenCommandHandler(BaseCommandHandler[RefreshTokenCommand, TokenGroup]):
    session: AsyncSession
    token_repository: SessionRepository

    async def handle(self, command: RefreshTokenCommand) -> TokenGroup:
        refresh_data = verify_token(token=command.refresh_token, token_type="refresh")
        token = await self.token_repository.get_by_jti(refresh_data.jti)

        if not token or not token.is_valid():
            raise InvalidJWTTokenException()

        new_access_token = create_access_token(
            data={"sub": str(token.user_id), 'device_id': token.device_id},
        )

        await self.session.commit()

        logger.info("Refresh token", extra={"sub": str(token.user_id), 'device_id': token.device_id})
        return TokenGroup(
            access_token=new_access_token,
            refresh_token=command.refresh_token,
        )
