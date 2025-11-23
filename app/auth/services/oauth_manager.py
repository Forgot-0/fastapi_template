from dataclasses import dataclass, field

from app.auth.schemas.token import OAuthData
from app.auth.services.oauth_providers import OAuthProvider


@dataclass
class OAuthProviderFactory:
    providers: dict[str, OAuthProvider] = field(default_factory=dict)

    def get_provider(self, provider_name: str) -> OAuthProvider:
        provider = self.providers.get(provider_name)
        if not provider:
            raise 
        return provider

    def register_provider(self, provider: OAuthProvider) -> None:
        self.providers[provider.name] = provider


@dataclass
class OAuthManager:
    provider_factory: OAuthProviderFactory

    async def get_authorize_url(self, provider_name: str, state: str) -> str:
        provider = self.provider_factory.get_provider(provider_name)
        return provider.get_auth_url(state)

    async def process_callback(self, provider_name: str, code: str) -> OAuthData:
        provider = self.provider_factory.get_provider(provider_name)

        token = await provider.exchange_code_for_token(code)
        oauth_user = await provider.get_user_info(token.access_token)

        return oauth_user