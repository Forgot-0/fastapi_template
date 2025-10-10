from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import WrongDataException
from app.auth.repositories.user import UserRepository
from app.auth.schemas.token import TokenGroup
from app.auth.schemas.user import UserJWTData
from app.auth.services.hash import HashService
from app.auth.services.jwt import JWTManager
from app.auth.services.session import SessionManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class LoginCommand(BaseCommand):
    username: str
    password: str
    user_agent: str


@dataclass(frozen=True)
class LoginCommandHandler(BaseCommandHandler[LoginCommand, TokenGroup]):
    session: AsyncSession
    user_repository: UserRepository
    session_manager: SessionManager
    jwt_manager: JWTManager
    hash_service: HashService

    async def handle(self, command: LoginCommand) -> TokenGroup:
        user = await self.user_repository.get_by_username(command.username) or \
        await self.user_repository.get_by_email(command.username)

        if not user or not self.hash_service.verify_password(command.password, user.password_hash):
            raise WrongDataException()

        session = await self.session_manager.get_or_create_session(
            user_id=user.id, user_agent=command.user_agent
        )

        await self.session.commit()
        token_group =  self.jwt_manager.create_token_pair(
            UserJWTData.create_from_user(user, device_id=session.device_id)
        )

        logger.info("Logining user", extra={"user_id": user.id, "device_id": session.device_id})
        return token_group