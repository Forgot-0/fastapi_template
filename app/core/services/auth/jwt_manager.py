from dataclasses import dataclass
from typing import Any

import jwt

from app.core.configs.app import app_config
from app.core.services.auth.dto import JwtTokenType, Token
from app.core.services.auth.exceptions import ExpiredTokenError, InvalidTokenError


@dataclass
class JWTManager:

    def encode(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, app_config.JWT_SECRET_KEY, algorithm=app_config.JWT_ALGORITHM)

    def decode(self, token: str) -> dict[str, Any]:
        try:
            data = jwt.decode(token, app_config.JWT_SECRET_KEY, algorithms=[app_config.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError as err:
            raise ExpiredTokenError(token=token) from err
        except jwt.PyJWTError as err:
            raise InvalidTokenError(token=token) from err
        return data

    async def validate_token(self, token: str, token_type: JwtTokenType=JwtTokenType.ACCESS) -> Token:
        payload = self.decode(token)
        token_data = Token(**payload)

        if token_data.type != token_type:
            raise InvalidTokenError(token=token)

        return token_data

