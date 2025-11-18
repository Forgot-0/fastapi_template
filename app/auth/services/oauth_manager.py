import logging
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs, urlencode

import httpx

from app.auth.exceptions import OAuthException
from app.auth.repositories.oauth import OAuthCodeRepository
from app.auth.services.providers import OAuthProvider


@dataclass
class OAuthProviderFactory:
    providers: dict[str, OAuthProvider] = field(default_factory=dict)

    def get_provider(self, provider_name: str) -> OAuthProvider:
        provider = self.providers.get(provider_name)
        if not provider:
            raise OAuthException()
        return provider

    def register_provider(self, provider: OAuthProvider) -> None:
        self.providers[provider.name] = provider


@dataclass
class OAuthManager:
    provider_factory: OAuthProviderFactory
    repository: OAuthCodeRepository
