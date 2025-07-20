from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.token import TokenRepository
from app.auth.security import create_access_token, verify_token
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class RefreshTokenCommand(BaseCommand):
    refresh_token: str


@dataclass(frozen=True)
class RefreshTokenCommandHandler(BaseCommandHandler[RefreshTokenCommand, str]):
    session: AsyncSession
    token_repository: TokenRepository

    async def handle(self, command: RefreshTokenCommand) -> str:
        payload = verify_token(command.refresh_token, token_type='refresh')

        token_obj = await self.token_repository.get_with_user(self.session, jti=payload.jti)
        if token_obj is None:
            raise

        if not token_obj.is_valid():
            raise

        new_access_token = create_access_token(
            data={"sub": str(token_obj.user_id), 'device_id': payload.device_id},
        )
        return new_access_token
