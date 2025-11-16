from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidJWTTokenException
from app.auth.repositories.session import SessionRepository
from app.auth.schemas.token import TokenGroup, TokenType
from app.auth.schemas.user import UserJWTData
from app.auth.services.jwt import JWTManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RefreshTokenCommand(BaseCommand):
    refresh_token: str | None
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class RefreshTokenCommandHandler(BaseCommandHandler[RefreshTokenCommand, TokenGroup]):
    session: AsyncSession
    jwt_manager: JWTManager
    session_repository: SessionRepository

    async def handle(self, command: RefreshTokenCommand) -> TokenGroup:
        if command.refresh_token is None:
            raise

        refresh_data = await self.jwt_manager.validate_token(command.refresh_token, TokenType.REFRESH)
        session = await self.session_repository.get_active_by_device(
            user_id=int(refresh_data.sub),
            device_id=refresh_data.did,
        )

        if not session or session.is_active == False:
            raise InvalidJWTTokenException()

        session.online()
        token_group = await self.jwt_manager.refresh_tokens(
            command.refresh_token, command.user_jwt_data
        )

        await self.session.commit()
        return token_group
