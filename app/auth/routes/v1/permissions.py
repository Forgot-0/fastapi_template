from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status

from app.auth.commands.permissions.create import CreatePermissionCommand
from app.auth.commands.permissions.delete import DeletePermissionCommand
from app.auth.deps import CurrentUserJWTData
from app.auth.exceptions import AccessDeniedException, NotFoundPermissionsException, ProtectedPermissionException
from app.auth.queries.permissions.get_list import GetListPemissionsQuery
from app.auth.schemas.permission.requests import PermissionCreateRequest
from app.auth.schemas.permissions import PermissionDTO, PermissionFilterParam, PermissionListParams, PermissionSortParam
from app.core.api.builder import ListParamsBuilder, create_response
from app.core.api.schemas import PaginatedResult
from app.core.mediators.base import BaseMediator

router = APIRouter(route_class=DishkaRoute)

list_params_builder = ListParamsBuilder(PermissionSortParam, PermissionFilterParam, PermissionListParams)



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
    user_jwt_data: CurrentUserJWTData
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
    user_jwt_data: CurrentUserJWTData
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
    user_jwt_data: CurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
    params: Annotated[PermissionListParams, Depends(list_params_builder)],
) -> PaginatedResult[PermissionDTO]:
    list_permission: PaginatedResult[PermissionDTO]
    list_permission = await mediator.handle_query(
        GetListPemissionsQuery(
            user_jwt_data=user_jwt_data,
            permission_query=params
        )
    )
    return list_permission
