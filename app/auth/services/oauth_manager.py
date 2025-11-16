from dataclasses import dataclass
import httpx
import logging

from app.auth.exceptions import NotExsistProviderException
from app.auth.models.oauth import OAuthProvider
from app.auth.repositories.oauth import OauthAccountRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.oauth import OAuthCallbackData


logger = logging.getLogger(__name__)


@dataclass
class OAuthProviderFactory:
    providers: dict[str, OAuthProvider]

    def get_provider(self, provider_name: str) -> OAuthProvider:
        if provider_name not in self.providers:
            raise NotExsistProviderException(provider_name)
        return self.providers[provider_name]


@dataclass
class OAuthManager:
    oauth_provider: OAuthProviderFactory
    oauth_repository: OauthAccountRepository
    user_repository: UserRepository

    async def get_user_info(
        self, provider: OAuthProvider, code: str
    ) -> OAuthCallbackData:
        access_token = await self._exchange_code_for_token(provider, code)

        user_info = await self._get_user_info_from_provider(provider, access_token)

        return user_info

    async def _exchange_code_for_token(self, provider: OAuthProvider, code: str) -> str:
        async with httpx.AsyncClient() as client:
            if provider.name == "google":
                response = await client.post(
                    provider.token_url,
                    data={
                        "code": code,
                        "client_id": provider.client_id,
                        "client_secret": provider.client_secret,
                        "redirect_uri": provider.redirect_uri,
                        "grant_type": "authorization_code",
                    }
                )
            elif provider.name == "yandex":
                response = await client.post(
                    provider.token_url,
                    data={
                        "code": code,
                        "client_id": provider.client_id,
                        "client_secret": provider.client_secret,
                        "grant_type": "authorization_code",
                    }
                )
            elif provider.name == "github":
                response = await client.post(
                    provider.token_url,
                    headers={"Accept": "application/json"},
                    data={
                        "code": code,
                        "client_id": provider.client_id,
                        "client_secret": provider.client_secret,
                        "redirect_uri": provider.redirect_uri,
                    }
                )
            else:
                raise NotExsistProviderException(provider.name)

            response.raise_for_status()
            token_data = response.json()
            return token_data.get("access_token")

    async def _get_user_info_from_provider(
        self, provider: OAuthProvider, access_token: str
    ) -> OAuthCallbackData:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.get(provider.userinfo_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if provider.name == "google":
                return OAuthCallbackData(
                    provider_user_id=data.get("sub"),
                    provider_email=data.get("email"),
                    name=data.get("name")
                )
            elif provider.name == "yandex":
                return OAuthCallbackData(
                    provider_user_id=data.get("id"),
                    provider_email=data.get("default_email"),
                    name=data.get("display_name")
                )
            elif provider.name == "github":
                return OAuthCallbackData(
                    provider_user_id=str(data.get("id")),
                    provider_email=data.get("email"),
                    name=data.get("name")
                )
            else:
                raise NotExsistProviderException(provider.name)

