from dataclasses import dataclass
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt

from app.core.services.auth.dto import JwtTokenType, Token
from app.core.services.auth.exceptions import ExpiredTokenException, InvalidTokenException


@dataclass
class JWTManager:
    jwt_secret: str
    jwt_algorithm: str

    def decode(self, token: str) -> dict[str, Any]:
        try:
            data = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        except ExpiredSignatureError as err:
            raise ExpiredTokenException(token=token) from err
        except JWTError as err:
            raise InvalidTokenException(token=token) from err
        return data

    async def validate_token(self, token: str, token_type: JwtTokenType=JwtTokenType.ACCESS) -> Token:
        payload = self.decode(token)
        token_data = Token(**payload)

        if token_data.type != token_type:
            raise InvalidTokenException(token=token)

        return token_data

