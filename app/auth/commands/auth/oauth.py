import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import (
    LinkedAnotherUserOAuthException,
    NotFoundRoleException,
    NotFoundUserException,
    OAuthStateNotFoundException,
)
from app.auth.models.oauth import OAuthAccount, OAuthProviderEnum
from app.auth.models.role_permission import RolesEnum
from app.auth.models.user import User
from app.auth.repositories.oauth import OauthAccountRepository, OAuthCodeRepository
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.tokens import TokenGroup
from app.auth.schemas.user import UserJWTData
from app.auth.services.jwt import JWTManager
from app.auth.services.oauth_manager import OAuthManager
from app.auth.services.session import SessionManager
from app.core.commands import BaseCommand, BaseCommandHandler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessOAuthCallbackCommand(BaseCommand):
    provider: str
    code: str
    state: str
    user_agent: str


@dataclass(frozen=True)
class ProcessOAuthCallbackCommandHandler(BaseCommandHandler[ProcessOAuthCallbackCommand, TokenGroup]):
    session: AsyncSession
    jwt_manager: JWTManager
    oauth_manager: OAuthManager
    user_repository: UserRepository
    role_repository: RoleRepository
    session_manager: SessionManager
    oauth_repository: OauthAccountRepository
    oauth_code_repository: OAuthCodeRepository

    async def handle(self, command: ProcessOAuthCallbackCommand) -> TokenGroup:
            oauth_data = await self.oauth_manager.process_callback(command.provider, command.code)
            user_id = await self.oauth_code_repository.get_state(command.state)

            if user_id is None:
                raise OAuthStateNotFoundException(state=command.state)

            oauth_account = await self.oauth_repository.get_by_provider_and_user_id(
                provider=OAuthProviderEnum(command.provider), provider_user_id=oauth_data.provider_user_id
            )

            if user_id != 0:
                if oauth_account and oauth_account.user_id != user_id:
                    raise LinkedAnotherUserOAuthException(provider=command.provider)

                if not oauth_account:
                    oauth_account = OAuthAccount(
                        provider=OAuthProviderEnum(command.provider),
                        provider_email=oauth_data.email,
                        provider_user_id=oauth_data.provider_user_id,
                        user_id=user_id
                    )
                    await self.oauth_repository.create(oauth_account)

                user = await self.user_repository.get_user_with_permission_by_id(user_id)
                if not user:
                    raise NotFoundUserException(user_by=user_id, user_field="id")

            elif oauth_account:
                user = await self.user_repository.get_user_with_permission_by_id(oauth_account.user_id)

                if not user:
                    raise NotFoundUserException(user_by=user_id, user_field="id")

                user_id = oauth_account.user_id

            else:
                role = await self.role_repository.get_with_permission_by_name(
                    RolesEnum.STANDARD_USER.value.name
                )
                if not role:
                    raise NotFoundRoleException(name=RolesEnum.STANDARD_USER.value.name)

                user = User.create_oauth(
                    email=oauth_data.email,
                    username=oauth_data.email,
                    roles={role }
                )
                await self.user_repository.create(user)
                await self.session.commit()

                user_id = user.id
                oauth_account = OAuthAccount(
                    provider=OAuthProviderEnum(command.provider),
                    provider_email=oauth_data.email,
                    provider_user_id=oauth_data.provider_user_id,
                    user_id=user_id
                )
                await self.oauth_repository.create(oauth_account)

            session = await self.session_manager.get_or_create_session(
                user_id=user_id, user_agent=command.user_agent
            )
            await self.oauth_code_repository.delete(command.state)
            await self.session.commit()
            token_group = self.jwt_manager.create_token_pair(
                UserJWTData.create_from_user(user, device_id=session.device_id)
            )

            logger.info(
                "OAuth Callback",
                extra={
                    "provider": command.provider,
                    "oauth_id": getattr(oauth_account, "id", None),
                    "user_id": user_id
                }
            )

            return token_group
