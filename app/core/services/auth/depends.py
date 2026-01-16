from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.services.auth.dto import UserJWTData
from app.core.services.auth.jwt_manager import JWTManager

security = HTTPBearer()


class UserJWTDataGetter:
    @inject
    async def __call__(
        self,
        jwt_manager: FromDishka[JWTManager],
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> UserJWTData:

        user_jwt_data = UserJWTData.create_from_token(
            await jwt_manager.validate_token(credentials.credentials)
        )
        return user_jwt_data

CurrentUserJWTData = Annotated[UserJWTData, Depends(UserJWTDataGetter())]

