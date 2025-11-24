from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status

from app.auth.commands.sessions.deactivate_session import UserDeactivateSessionCommand
from app.auth.deps import CurrentUserJWTData
from app.auth.exceptions import AccessDeniedException, NotFoundOrInactiveSessionException
from app.auth.queries.sessions.get_list import GetListSessionQuery
from app.auth.schemas.sessions import SessionDTO, SessionFilterParam, SessionListParams, SessionSortParam
from app.core.api.builder import ListParamsBuilder, create_response
from app.core.api.schemas import PaginatedResult
from app.core.mediators.base import BaseMediator

router = APIRouter(route_class=DishkaRoute)


list_params_builder = ListParamsBuilder(SessionSortParam, SessionFilterParam, SessionListParams)



@router.delete(
    "/{session_id}",
    summary="Log out of session",
    description="Log out of session",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response(NotFoundOrInactiveSessionException()),
    }
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

@router.get(
    "/",
    summary="Get a list of sessions",
    description="Get a list of sessions",
    status_code=status.HTTP_200_OK,
    responses={
        403: create_response(AccessDeniedException(need_permissions={"string" }))
    }
)
async def get_list_sessions(
    user_jwt_data: CurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
    params: Annotated[SessionListParams, Depends(list_params_builder)],
) -> PaginatedResult[SessionDTO]:
    result: PaginatedResult[SessionDTO]
    result = await mediator.handle_query(
        GetListSessionQuery(
            session_query=params,
            user_jwt_data=user_jwt_data
        )
    )
    return result
