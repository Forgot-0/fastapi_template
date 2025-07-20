from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.token import TokenRepository
from app.auth.security import verify_token
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class LogoutCommand(BaseCommand):
    refresh_token: str


@dataclass(frozen=True)
class LogoutCommandHandler(BaseCommandHandler[LogoutCommand, None]):
    session: AsyncSession
    token_repository: TokenRepository

    async def handle(self, command: LogoutCommand) -> None:
        payload = verify_token(command.refresh_token, token_type='refresh')
        await self.token_repository.revoke_user_device(
            self.session, user_id=int(payload.sub), jti=payload.jti
        )
        await self.session.commit()