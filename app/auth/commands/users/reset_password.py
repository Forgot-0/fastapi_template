from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.user import UserRepository
from app.auth.security import decode_reset_token, hash_password
from app.core.command import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class ResetPasswordCommand(BaseCommand):
    token: str
    password: str
    repeat_password: str


@dataclass(frozen=True)
class ResetPasswordCommandHandler(BaseCommandHandler[ResetPasswordCommand, None]):
    session: AsyncSession
    user_repository: UserRepository

    async def handle(self, command: ResetPasswordCommand) -> None:
        reset_token = decode_reset_token(token=command.token)
        user = await self.user_repository.get_by_email(self.session, email=reset_token.sub)

        if not user: return

        if command.password != command.repeat_password:
            raise

        user.password_hash = hash_password(command.password)
        await self.session.commit()
