from typing import Annotated, Any
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.models.user import User
from app.auth.schemas.user import UserDTO
from app.auth.services.tokens import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", refreshUrl="/api/v1/auth/refresh")


class CurrentUserGetter:
    @inject
    async def __call__(
        self,
        token_service: FromDishka[AuthService],
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> UserDTO:
        try:
            user: User = await token_service.get_user_by_token(token=token)
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        user_dto = UserDTO.model_validate(user.to_dict())
        return user_dto

class ActiveUserGetter:
    async def __call__(self, user: Annotated[UserDTO, Depends(CurrentUserGetter())]) -> UserDTO:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Inactive user',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        return user

class ActiveUserGetterWebsoket:
    async def __call__(
        self,
        token_service: AuthService,
        websocket: WebSocket
    ) -> UserDTO:
        try:
            token = websocket.headers.get("sec-websocket-protocol")
            if not token: raise
            token = token[13:]
            user: User = await token_service.get_user_by_token(token=token)
            if not user.is_active:
                raise
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        return UserDTO.model_validate(user.to_dict())


CurrentUserModel = Annotated[UserDTO, Depends(CurrentUserGetter())]
ActiveUserModel = Annotated[UserDTO, Depends(ActiveUserGetter())]
