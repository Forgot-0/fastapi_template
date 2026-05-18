from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, status

from app.auth.commands.sessions.deactivate_session import UserDeactivateSessionCommand
from app.auth.deps import AuthCurrentUserJWTData
from app.auth.dtos.sessions import SessionDTO
from app.auth.exceptions import NotFoundOrInactiveSessionException
from app.auth.queries.sessions.get_list import GetListSessionQuery
from app.auth.schemas.sessions.requests import GetSessionsRequest
from app.core.api.builder import create_response
from app.core.db.repository import PageResult
from app.core.mediators.base import BaseMediator
from app.core.services.auth.exceptions import AccessDeniedException

router = APIRouter(route_class=DishkaRoute)



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
    user_jwt_data: AuthCurrentUserJWTData,
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
    user_jwt_data: AuthCurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
    params: GetSessionsRequest=Query(),
) -> PageResult[SessionDTO]:
    result: PageResult[SessionDTO]
    result = await mediator.handle_query(
        GetListSessionQuery(
            session_filter=params.to_session_filter(),
            user_jwt_data=user_jwt_data
        )
    )
    return result
