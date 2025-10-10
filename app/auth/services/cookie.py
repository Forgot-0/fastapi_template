from dataclasses import dataclass
from typing import Literal

from fastapi import Request, Response


@dataclass
class CookieManager:
    cookie_path: str
    cookie_secure: bool
    cookie_httponly: bool
    cookie_samesite: Literal['lax', 'strict', 'none'] | None
    cookie_max_age: int

    def set_cookie(
        self,
        response: Response,
        token: str,
        max_age: int | None = None,
        key: str = "refresh_token",
    ) -> None:
        response.set_cookie(
            key=key,
            value=token,
            max_age=max_age or self.cookie_max_age,
            path=self.cookie_path,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )

    def delete_cookie(self, response: Response, key: str) -> None:
        response.delete_cookie(
            key=key,
            path=self.cookie_path,
        )

    def get_cookie(self, request: Request, key: str) -> str | None:
        return request.cookies.get(key)
