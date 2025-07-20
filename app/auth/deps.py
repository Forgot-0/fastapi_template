from typing import Annotated
from dishka import FromDishka
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.models.user import User
from app.auth.queries.auth.get_by_token import GetByAcccessTokenQuery
from app.core.mediators.base import BaseMediator


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class CurrentUserGetter:
    async def __call__(
        self,
        mediator: FromDishka[BaseMediator],
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> User:
        try:
            user: User = await mediator.handle_query(GetByAcccessTokenQuery(token=token))
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return user

class ActiveUserGetter:
    async def __call__(self, user: Annotated[User, Depends(CurrentUserGetter())]) -> User:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Inactive user',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        return user

CurrentUserModel = Annotated[User, Depends(CurrentUserGetter())]
ActiveUserModel = Annotated[User, Depends(ActiveUserGetter())]