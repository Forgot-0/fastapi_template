from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import WrongDataException, NotFoundRoleException
from app.auth.models.oauth import OAuthAccount, OAuthProviderEnum
from app.auth.models.user import User
from app.auth.repositories.oauth import OauthAccountRepository
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.token import TokenGroup
from app.auth.schemas.user import UserJWTData
from app.auth.services.jwt import JWTManager
from app.auth.services.oauth_manager import OAuthManager
from app.auth.services.session import SessionManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OAuthLoginCommand(BaseCommand):
    code: str
    provider: str
    user_agent: str


@dataclass(frozen=True)
class OAuthLoginCommandHandler(BaseCommandHandler[OAuthLoginCommand, TokenGroup]):
    session: AsyncSession
    oauth_manager: OAuthManager
    user_repository: UserRepository
    oauth_repository: OauthAccountRepository
    session_manager: SessionManager
    jwt_manager: JWTManager
    role_repository: RoleRepository

    async def handle(self, command: OAuthLoginCommand) -> TokenGroup:
        provider = self.oauth_manager.oauth_provider.get_provider(command.provider)

        user_info = await self.oauth_manager.get_user_info(provider, command.code)

        oauth_account = await self.oauth_repository.get_by_provider_and_user_id(
            provider=OAuthProviderEnum[command.provider.upper()],
            provider_user_id=user_info.provider_user_id
        )

        if oauth_account:
            user = await self.user_repository.get_user_with_roles_by_id(oauth_account.user_id)
            if not user:
                raise WrongDataException()
        else:
            user = await self.user_repository.get_with_roles_by_email(user_info.provider_email)

            if not user:
                role = await self.role_repository.get_with_permission_by_name("user")
                if not role:
                    raise NotFoundRoleException("user")

                user = User(
                    email=user_info.provider_email,
                    username=user_info.provider_email.split('@')[0],
                    password_hash=None,
                    roles={role},
                    is_active=True,
                    is_verified=True,
                    permissions=set()
                )
                await self.user_repository.create(user)
                await self.session.flush()

            oauth_account = OAuthAccount(
                provider=OAuthProviderEnum[command.provider.upper()],
                provider_user_id=user_info.provider_user_id,
                provider_email=user_info.provider_email,
                is_active=True,
                user_id=user.id
            )
            await self.oauth_repository.create(oauth_account)

        session = await self.session_manager.get_or_create_session(
            user_id=user.id, user_agent=command.user_agent
        )

        await self.session.commit()

        token_group = self.jwt_manager.create_token_pair(
            UserJWTData.create_from_user(user, device_id=session.device_id)
        )

        logger.info(
            "OAuth login successful",
            extra={
                "user_id": user.id,
                "provider": command.provider,
                "device_id": session.device_id
            }
        )

        return token_group

