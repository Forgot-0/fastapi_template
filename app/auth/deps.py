from typing import Annotated
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.models.user import User
from app.auth.queries.auth.get_by_token import GetByAccessTokenQuery
from app.auth.schemas.user import UserDTO
from app.core.exceptions import ApplicationException
from app.core.mediators.base import BaseMediator


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", refreshUrl="/api/v1/auth/refresh")


class CurrentUserGetter:
    @inject
    async def __call__(
        self,
        mediator: FromDishka[BaseMediator],
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> UserDTO:
        try:
            user: User = await mediator.handle_query(
                GetByAccessTokenQuery(token=token)
            )
        except ApplicationException:
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


CurrentUserModel = Annotated[UserDTO, Depends(CurrentUserGetter())]
ActiveUserModel = Annotated[UserDTO, Depends(ActiveUserGetter())]
