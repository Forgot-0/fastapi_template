from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas.token import TokenGroup
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

    async def handle(self, command: RefreshTokenCommand) -> TokenGroup:
        if command.refresh_token is None:
            raise

        token_group = await self.jwt_manager.refresh_tokens(
            command.refresh_token,
        )

        await self.session.commit()
        return token_group
