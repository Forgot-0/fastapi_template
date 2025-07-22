from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.events.users.created import CreatedUserEvent
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserCreate, UserDTO
from app.auth.security import hash_password
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.events.service import BaseEventBus


@dataclass(frozen=True)
class RegisterCommand(BaseCommand):
    username: str
    email: str
    password: str
    password_repeat: str


@dataclass(frozen=True)
class RegisterCommandHandler(BaseCommandHandler[RegisterCommand, UserDTO]):
    session: AsyncSession
    event_bus: BaseEventBus
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
        await self.session.refresh(user)
        await self.event_bus.publish(
            [
                CreatedUserEvent(user_id=user.id, email=user.email)
            ]
        )
        await self.session.commit()
        return UserDTO.model_validate(user.to_dict())