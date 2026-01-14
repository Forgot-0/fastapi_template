from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.services.auth.dto import UserJWTData
from app.core.services.auth.exceptions import NotAuthenticatedException
from app.core.services.auth.jwt_manager import JWTManager


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    refreshUrl="/api/v1/auth/refresh",
    auto_error=False
)


class UserJWTDataGetter:
    @inject
    async def __call__(
        self,
        jwt_manager: FromDishka[JWTManager],
        token: Annotated[str | None, Depends(oauth2_scheme)],
    ) -> UserJWTData:
        if token is None:
            raise NotAuthenticatedException

        user_jwt_data = UserJWTData.create_from_token(
            await jwt_manager.validate_token(token)
        )
        return user_jwt_data


CurrentUserJWTData = Annotated[UserJWTData, Depends(UserJWTDataGetter())]

