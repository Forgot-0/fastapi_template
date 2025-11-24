import logging
import secrets
from dataclasses import dataclass

from app.auth.repositories.oauth import OAuthCodeRepository
from app.auth.services.oauth_manager import OAuthManager
from app.core.commands import BaseCommand, BaseCommandHandler

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class CreateOAuthAuthorizeUrlCommand(BaseCommand):
    provider: str
    user_id: int | None


@dataclass(frozen=True)
class CreateOAuthAuthorizeUrlCommandHandler(BaseCommandHandler[CreateOAuthAuthorizeUrlCommand, str]):
    oauth_code_repository: OAuthCodeRepository
    oauth_manager: OAuthManager

    async def handle(self, command: CreateOAuthAuthorizeUrlCommand) -> str:
        state = secrets.token_urlsafe(32)
        await self.oauth_code_repository.add_oauth_state(state, command.user_id)

        logger.info("Login by oauth", extra={"provider": command.provider, "user_id": command.user_id})
        return await self.oauth_manager.get_authorize_url(
            provider_name=command.provider, state=state
        )
