from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.user import UserRepository
from app.auth.security import decode_verify_token
from app.core.command import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class VerifyCommand(BaseCommand):
    token: str


@dataclass(frozen=True)
class VerifyCommandHandler(BaseCommandHandler[VerifyCommand, None]):
    session: AsyncSession
    user_repository: UserRepository

    async def handle(self, command: VerifyCommand) -> None:
        verify_token = decode_verify_token(token=command.token)
        user = await self.user_repository.get_by_email(self.session, email=verify_token.sub)

        if not user:
            raise

        user.is_verified = True
        await self.session.commit()