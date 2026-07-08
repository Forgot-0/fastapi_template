import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dtos.tokens import TokenGroup
from app.auth.dtos.user import AuthUserJWTData
from app.auth.exceptions import NotFoundOrInactiveSessionError, NotFoundUserError, TokenInBlacklistError
from app.auth.repositories.session import SessionRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.jwt import AuthJWTManager
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.services.auth.dto import JwtTokenType
from app.core.services.auth.exceptions import InvalidTokenError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RefreshTokenCommand(BaseCommand):
    refresh_token: str | None
    ip_adress: str


@dataclass(frozen=True)
class RefreshTokenCommandHandler(BaseCommandHandler[RefreshTokenCommand, TokenGroup]):
    session: AsyncSession
    jwt_manager: AuthJWTManager
    session_repository: SessionRepository
    user_repository: UserRepository

    async def handle(self, command: RefreshTokenCommand) -> TokenGroup:
        if command.refresh_token is None:
            raise InvalidTokenError(token=None)

        refresh_token = await self.jwt_manager.validate_token(command.refresh_token, JwtTokenType.REFRESH)
        session = await self.session_repository.get_active_by_device(
            user_id=int(refresh_token.sub),
            device_id=refresh_token.did,
        )

        if not session or not session.is_active:
            raise NotFoundOrInactiveSessionError

        session.online()

        user = await self.user_repository.get_user_with_permission_by_id(
                int(refresh_token.sub)
            )
        if user is None:
            raise NotFoundUserError(user_field="id", user_by="")

        user_jwt_data = AuthUserJWTData.create_from_user(
            user, refresh_token.did
        )

        try:
            token_group = await self.jwt_manager.refresh_tokens(
                refresh_token, user_jwt_data
            )
        except TokenInBlacklistError:
            session.deactivate()
            await self.session.commit()
            raise

        await self.session.commit()
        return token_group
