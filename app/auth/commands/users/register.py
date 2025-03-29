from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserCreate, UserDTO
from app.auth.security import hash_password
from app.core.command import BaseCommand, BaseCommandHandler
from app.core.event_bus import EventBus


@dataclass(frozen=True)
class RegisterCommand(BaseCommand):
    username: str
    email: str
    password: str
    password_repeat: str


@dataclass(frozen=True)
class RegisterCommandHandler(BaseCommandHandler[RegisterCommand, UserDTO]):
    session: AsyncSession
    event_bus: EventBus
    user_repository: UserRepository

    async def handle(self, command: RegisterCommand) -> UserDTO:
        if command.password != command.password_repeat:
            raise

        data = UserCreate(
            email=command.email,
            username=command.username,
            password_hash=hash_password(command.password)
        )

        user = await self.user_repository.create(self.session, data=data)
        await self.session.commit()
        await self.session.refresh(user)
        return UserDTO.model_validate(**user.to_dict())