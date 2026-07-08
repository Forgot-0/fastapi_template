import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dtos.tokens import TokenGroup
from app.auth.dtos.user import AuthUserJWTData
from app.auth.exceptions import WrongLoginDataError
from app.auth.repositories.user import UserRepository
from app.auth.services.hash import HashService
from app.auth.services.jwt import AuthJWTManager
from app.auth.services.session import SessionManager
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.events.service import BaseEventBus

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class LoginCommand(BaseCommand):
    username: str
    password: str
    user_agent: str
    ip_adress: str


@dataclass(frozen=True)
class LoginCommandHandler(BaseCommandHandler[LoginCommand, TokenGroup]):
    session: AsyncSession
    user_repository: UserRepository
    session_manager: SessionManager
    jwt_manager: AuthJWTManager
    hash_service: HashService
    event_bus: BaseEventBus

    async def handle(self, command: LoginCommand) -> TokenGroup:
        if "@" in command.username:
            user = await self.user_repository.get_with_roles_by_email(command.username)
        else:
            user = await self.user_repository.get_with_roles_by_username(command.username)

        if (
            (user is None) or
            (user.password_hash is None) or
            (not self.hash_service.verify_password(command.password, user.password_hash))
        ):
            raise WrongLoginDataError(username=command.username)

        session = await self.session_manager.get_or_create_session(
            user_id=user.id, user_agent=command.user_agent, ip_adress=command.ip_adress
        )

        await self.session.commit()
        await self.event_bus.publish(session.pull_events())

        token_group = self.jwt_manager.create_token_pair(
            AuthUserJWTData.create_from_user(user, device_id=session.device_id)
        )

        logger.info("Logining user", extra={"user_id": user.id, "device_id": session.device_id})
        return token_group
