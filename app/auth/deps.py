from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.commands.users.register import RegisterCommand, RegisterCommandHandler
from app.auth.models.user import User

from app.auth.queries.auth.get_by_token import GetByAcccessTokenQuery, GetByAcccessTokenQueryHandler
from app.auth.repositories.token import TokenRepository
from app.auth.repositories.user import UserRepository

from app.core.event_bus import EventBus as EventBusCls
from app.core.mediator import Mediator as MediatorCls
from app.core.configs.app import app_config
from app.core.depends import Asession, MailService

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f'{app_config.API_V1_STR}/auth/login')

user_repository = UserRepository()
token_repository = TokenRepository()


async def get_auth_event_bus(session: Asession, mail_service: MailService) -> EventBusCls:
    event_bus = EventBusCls()

    return event_bus

async def get_auth_mediator(
        event_bus: Annotated[EventBusCls, Depends(get_auth_event_bus)],
        session: Asession, 
        mail_service: MailService,
    ) -> MediatorCls:
    mediator = MediatorCls()

    # AUTH
    mediator.register_query(
        GetByAcccessTokenQuery,
        GetByAcccessTokenQueryHandler(session=session, user_repository=user_repository)
    )

    # USER
    mediator.register_command(
        RegisterCommand,
        RegisterCommandHandler(session=session, event_bus=event_bus, user_repository=user_repository)
    )

    return mediator


class CurrentUserGetter:
    async def __call__(
        self,
        mediator: Annotated[MediatorCls, Depends(get_auth_mediator)],
        token: Annotated[str, Depends(reusable_oauth2)],
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


Mediator = Annotated[MediatorCls, Depends(get_auth_mediator)]

CurrentUserModel = Annotated[User, Depends(CurrentUserGetter())]
ActiveUserModel = Annotated[User, Depends(ActiveUserGetter())]

