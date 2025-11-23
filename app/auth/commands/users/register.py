from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.role_permission import RolesEnum
from app.auth.models.user import User
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserDTO
from app.auth.services.hash import HashService
from app.auth.exceptions import DuplicateUserException, PasswordMismatchException, NotFoundRoleException
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.events.service import BaseEventBus


logger = logging.getLogger(__name__)

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
    role_repository: RoleRepository
    hash_service: HashService

    async def handle(self, command: RegisterCommand) -> UserDTO:
        user = await self.user_repository.get_by_username(command.username)

        if user:
            raise DuplicateUserException(field="username", value=command.username)

        user = await self.user_repository.get_by_email(command.email)
        if user:
            raise DuplicateUserException(field="email", value=command.email)

        if command.password != command.password_repeat:
            raise PasswordMismatchException()

        role = await self.role_repository.get_with_permission_by_name(
            RolesEnum.STANDARD_USER.value.name
        )
        if not role:
            raise NotFoundRoleException(name=RolesEnum.STANDARD_USER.value.name)

        user = User.create(
            email=command.email,
            username=command.username,
            password_hash=self.hash_service.hash_password(command.password),
            roles={role, }
        )
        await self.user_repository.create(user)

        await self.session.commit()
        await self.event_bus.publish(user.pull_events())

        user_dto = UserDTO.model_validate(user.to_dict())
        logger.info("Register user", extra={"user": user_dto.model_dump()})
        return user_dto