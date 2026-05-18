from typing import TYPE_CHECKING, Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.dtos.user import AuthUserJWTData, UserDTO
from app.auth.queries.auth.get_by_token import GetByAccessTokenQuery
from app.core.mediators.base import BaseMediator
from app.core.services.auth.depends import UserJWTDataGetter
from app.core.services.auth.exceptions import AccessDeniedException, NotAuthenticatedException

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
        token: Annotated[str | None, Depends(oauth2_scheme)],
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


AuthCurrentUserJWTData = Annotated[AuthUserJWTData, Depends(UserJWTDataGetter())]

