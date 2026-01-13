import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidTokenException, NotFoundOrInactiveSessionException, NotFoundUserException
from app.auth.repositories.session import SessionRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.tokens import TokenGroup, TokenType
from app.auth.schemas.user import UserJWTData
from app.auth.services.jwt import JWTManager
from app.core.commands import BaseCommand, BaseCommandHandler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RefreshTokenCommand(BaseCommand):
    refresh_token: str | None


@dataclass(frozen=True)
class RefreshTokenCommandHandler(BaseCommandHandler[RefreshTokenCommand, TokenGroup]):
    session: AsyncSession
    jwt_manager: JWTManager
    session_repository: SessionRepository
    user_repository: UserRepository

    async def handle(self, command: RefreshTokenCommand) -> TokenGroup:
        if command.refresh_token is None:
            raise InvalidTokenException(token=None)

        refresh_data = await self.jwt_manager.validate_token(command.refresh_token, TokenType.REFRESH)
        session = await self.session_repository.get_active_by_device(
            user_id=int(refresh_data.sub),
            device_id=refresh_data.did,
        )

        if not session or not session.is_active:
            raise NotFoundOrInactiveSessionException

        session.online()

        user = await self.user_repository.get_user_with_permission_by_id(
                int(refresh_data.sub)
            )
        if user is None:
            raise NotFoundUserException(user_field="id", user_by="")

        user_jwt_data = UserJWTData.create_from_user(
            user, session.device_id
        )

        token_group = await self.jwt_manager.refresh_tokens(
            command.refresh_token, user_jwt_data
        )

        await self.session.commit()
        return token_group
