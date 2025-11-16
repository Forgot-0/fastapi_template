
from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import WrongDataException
from app.auth.models.oauth import OAuthAccount, OAuthProviderEnum
from app.auth.repositories.oauth import OauthAccountRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.oauth_manager import OAuthManager
from app.core.commands import BaseCommand, BaseCommandHandler


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OAuthConnectCommand(BaseCommand):
    code: str
    provider: str
    user_id: int
    user_agent: str


@dataclass(frozen=True)
class OAuthConnectCommandHandler(BaseCommandHandler[OAuthConnectCommand, None]):
    session: AsyncSession
    oauth_manager: OAuthManager
    user_repository: UserRepository
    oauth_repository: OauthAccountRepository

    async def handle(self, command: OAuthConnectCommand) -> None:
        user = await self.user_repository.get_by_id(command.user_id)
        if not user:
            raise WrongDataException()

        provider = self.oauth_manager.oauth_provider.get_provider(command.provider)

        user_info = await self.oauth_manager.get_user_info(provider, command.code)

        existing_oauth = await self.oauth_repository.get_by_provider_and_user_id(
            provider=OAuthProviderEnum[command.provider.upper()],
            provider_user_id=user_info.provider_user_id
        )

        if existing_oauth and existing_oauth.user_id != command.user_id:
            raise WrongDataException()

        if existing_oauth:
            raise

        oauth_account = OAuthAccount(
            provider=OAuthProviderEnum[command.provider.upper()],
            provider_user_id=user_info.provider_user_id,
            provider_email=user_info.provider_email,
            is_active=True,
            user_id=command.user_id
        )
        await self.oauth_repository.create(oauth_account)
        await self.session.commit()

        logger.info(
            "OAuth account connected",
            extra={
                "user_id": command.user_id,
                "provider": command.provider
            }
        )