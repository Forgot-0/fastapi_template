from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas.token import TokenGroup
from app.auth.services.tokens import AuthService
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class RefreshTokenCommand(BaseCommand):
    refresh_token: str


@dataclass(frozen=True)
class RefreshTokenCommandHandler(BaseCommandHandler[RefreshTokenCommand, TokenGroup]):
    session: AsyncSession
    token_service: AuthService

    async def handle(self, command: RefreshTokenCommand) -> TokenGroup:
        token_group = await self.token_service.refresh_token(command.refresh_token)
        await self.session.commit()
        return token_group