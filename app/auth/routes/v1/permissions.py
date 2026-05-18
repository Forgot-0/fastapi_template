from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, status

from app.auth.commands.permissions.create import CreatePermissionCommand
from app.auth.commands.permissions.delete import DeletePermissionCommand
from app.auth.deps import AuthCurrentUserJWTData
from app.auth.dtos.permissions import PermissionDTO
from app.auth.exceptions import NotFoundPermissionsException, ProtectedPermissionException
from app.auth.queries.permissions.get_list import GetListPemissionsQuery
from app.auth.schemas.permission.requests import GetPermissionsRequest, PermissionCreateRequest
from app.core.api.builder import create_response
from app.core.db.repository import PageResult
from app.core.mediators.base import BaseMediator
from app.core.services.auth.exceptions import AccessDeniedException

router = APIRouter(route_class=DishkaRoute)




@router.post(
    "/",
    summary="Create a new permission",
    description="Creates a new permission",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response(NotFoundPermissionsException(missing={"string" })),
        409: create_response(ProtectedPermissionException(name="string"))
    }
)
async def create_permission(
    permission_request: PermissionCreateRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: AuthCurrentUserJWTData
) -> None:
    await mediator.handle_command(
        CreatePermissionCommand(
            name=permission_request.name,
            user_jwt_data=user_jwt_data
        )
    )


@router.delete(
    "/{name}",
    summary="Removing permission",
    description="Removes permission",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response(NotFoundPermissionsException(missing={"string" })),
        409: create_response(ProtectedPermissionException(name="string"))
    }
)
async def delete_permission(
    name: str,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: AuthCurrentUserJWTData
) -> None:
    await mediator.handle_command(
        DeletePermissionCommand(
            name=name,
            user_jwt_data=user_jwt_data
        )
    )


@router.get(
    "/",
    summary="Get a list of permissions",
    description="Get a list of permissions",
    responses={
        403: create_response(AccessDeniedException(need_permissions={"string" })),
    }
)
async def get_list_news(
    user_jwt_data: AuthCurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
    params: GetPermissionsRequest=Query(),
) -> PageResult[PermissionDTO]:
    list_permission: PageResult[PermissionDTO]
    list_permission = await mediator.handle_query(
        GetListPemissionsQuery(
            user_jwt_data=user_jwt_data,
            permission_filter=params.to_permission_filter()
        )
    )
    return list_permission
