from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.auth.commands.sessions.deactivate_session import UserDeactivateSessionCommand
from app.auth.deps import CurrentUserJWTData
from app.auth.schemas.sessions import SessionFilterParam, SessionListParams, SessionSortParam
from app.core.api.builder import ListParamsBuilder
from app.core.mediators.base import BaseMediator


router = APIRouter(route_class=DishkaRoute)


list_params_builder = ListParamsBuilder(SessionSortParam, SessionFilterParam, SessionListParams)



@router.delete(
    "/{session_id}",
    summary="Выйти из сессии",
    description="Выйти из сессии",
    status_code=status.HTTP_204_NO_CONTENT
)
async def user_session_delete(
    session_id: int,
    user_jwt_data: CurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
) -> None:
    await mediator.handle_command(
        UserDeactivateSessionCommand(
            session_id=session_id,
            user_jwt_data=user_jwt_data
        )
    )

