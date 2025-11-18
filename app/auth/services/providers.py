
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from app.auth.schemas.token import OAuthToken, OAuthData



@dataclass
class OAuthProvider(ABC):
    name: str
    client_id: str
    client_secret: str
    redirect_uri: str
    connect_url: str
    base_auth_url: str
    token_url: str
    userinfo_url: str

    @abstractmethod
    def get_auth_url(self, state: str) -> str: ...

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> OAuthToken:
        ...

    async def _exchange_code(self, data: dict[str, Any], headers: dict[str, Any]) -> OAuthToken:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=data,
                headers=headers
            )
            response.raise_for_status()
            token_data = response.json()
            return OAuthToken(
                access_token=token_data['access_token'],
                token_type=token_data.get('token_type', 'Bearer'),
                expires_in=token_data.get('expires_in'),
                refresh_token=token_data.get('refresh_token'),
                scope=token_data.get('scope')
            )

    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthData:
        ...

    async def _fetch_user_info(self, headers: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_url,
                headers=headers
            )
            response.raise_for_status()
            return response.json()


@dataclass
class OAuthGoogle(OAuthProvider):
    def get_auth_url(self, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        return f"{self.base_auth_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> OAuthToken:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        return await self._exchange_code(
            data=data,
            headers={"Accept": "application/json"}
        )

    async def get_user_info(self, access_token: str) -> OAuthData:
        user_data = await self._fetch_user_info(
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return OAuthData(
            provider_user_id=user_data["sub"],
            email=user_data["email"],
            username=user_data.get("name"),
        )


@dataclass
class OAuthYandex(OAuthProvider):
    def get_auth_url(self, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "force_confirm": "yes"
        }
        return f"{self.base_auth_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> OAuthToken:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        return await self._exchange_code(
            data=data,
            headers={"Accept": "application/json"}
        )

    async def get_user_info(self, access_token: str) -> OAuthData:
        user_data = await self._fetch_user_info(
            headers={"Authorization": f"OAuth {access_token}"}
        )
        email = user_data.get("default_email")
        if not email and user_data.get("emails"):
            email = user_data["emails"][0]

        return OAuthData(
            provider_user_id=user_data["id"],
            email=email, # pyright: ignore[reportArgumentType]
            username=user_data.get("login"),
        )



class OAuthGithub(OAuthProvider):
    def get_auth_url(self, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read:user,user:email",
            "state": state,
            "allow_signup": "false"
        }
        return f"{self.base_auth_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> OAuthToken:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        return await self._exchange_code(
            data=data,
            headers={"Accept": "application/json"}
        )

    async def get_user_info(self, access_token: str) -> OAuthData:
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }
        user_data = await self._fetch_user_info(
            headers=headers
        )
        return OAuthData(
            provider_user_id=str(user_data["id"]),
            email=await self._get_email(headers),
            username=user_data.get("login"),
        )

    async def _get_email(self, headers: dict[str, Any]) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.github.com/user/emails",
                headers=headers
            )
            response.raise_for_status()
            email_data = response.json()

            for email_data in email_data:
                if email_data.get("primary"):
                    return email_data.get("email")

            return email_data[0].get("email")

