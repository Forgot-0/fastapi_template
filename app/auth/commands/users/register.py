from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.events.users.created import CreatedUserEvent
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserCreate, UserDTO
from app.auth.security import hash_password
from app.auth.services.users import UserService
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.events.service import BaseEventBus


@dataclass(frozen=True)
class RegisterCommand(BaseCommand):
    data: UserCreate


@dataclass(frozen=True)
class RegisterCommandHandler(BaseCommandHandler[RegisterCommand, UserDTO]):
    session: AsyncSession
    event_bus: BaseEventBus
    user_service: UserService

    async def handle(self, command: RegisterCommand) -> UserDTO:
        user = await self.user_service.create(user_data=command.data)
        await self.session.commit()
        await self.session.refresh(user)

        await self.event_bus.publish(user.pull_events())
        return UserDTO.model_validate(user.to_dict())