from typing import TYPE_CHECKING, Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.exceptions import AccessDeniedException, NotAuthenticatedException
from app.auth.queries.auth.get_by_token import GetByAccessTokenQuery
from app.auth.queries.auth.verify import VerifyTokenQuery
from app.auth.schemas.user import UserDTO, UserJWTData
from app.core.mediators.base import BaseMediator

if TYPE_CHECKING:
    from app.auth.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    refreshUrl="/api/v1/auth/refresh",
    auto_error=False
)


class CurrentUserGetter:
    @inject
    async def __call__(
        self,
        mediator: FromDishka[BaseMediator],
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> UserDTO:
        if token is None:
            raise NotAuthenticatedException

        user: User = await mediator.handle_query(
            GetByAccessTokenQuery(token=token)
        )
        user_dto = UserDTO.model_validate(user.to_dict())
        return user_dto


class ActiveUserGetter:
    async def __call__(self, user: Annotated[UserDTO, Depends(CurrentUserGetter())]) -> UserDTO:
        if not user.is_active:
            raise AccessDeniedException(need_permissions=set())
        return user


CurrentUserModel = Annotated[UserDTO, Depends(CurrentUserGetter())]
ActiveUserModel = Annotated[UserDTO, Depends(ActiveUserGetter())]


class UserJWTDataGetter:
    @inject
    async def __call__(
        self,
        mediator: FromDishka[BaseMediator],
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> UserJWTData:
        if token is None:
            raise NotAuthenticatedException

        user_jwt_data: UserJWTData
        user_jwt_data = await mediator.handle_query(
            VerifyTokenQuery(token=token)
        )
        return user_jwt_data


CurrentUserJWTData = Annotated[UserJWTData, Depends(UserJWTDataGetter())]

