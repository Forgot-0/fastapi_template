from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.user import UserRepository
from app.auth.security import decode_reset_token, hash_password
from app.auth.services.users import UserService
from app.core.commands import BaseCommand, BaseCommandHandler


@dataclass(frozen=True)
class ResetPasswordCommand(BaseCommand):
    token: str
    password: str
    repeat_password: str


@dataclass(frozen=True)
class ResetPasswordCommandHandler(BaseCommandHandler[ResetPasswordCommand, None]):
    session: AsyncSession
    user_service: UserService

    async def handle(self, command: ResetPasswordCommand) -> None:
        await self.user_service.reset_password(
            token=command.token,
            password=command.password,
            repeat_password=command.repeat_password
        )
        await self.session.commit()
