from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status

from app.auth.commands.permissions.create import CreatePermissionCommand
from app.auth.commands.permissions.delete import DeletePermissionCommand
from app.auth.deps import CurrentUserJWTData
from app.auth.queries.permissions.get_list import GetListPemissionsQuery
from app.auth.schemas.permission.requests import PermissionCreateRequest, PermissionDeleteRequest
from app.auth.schemas.permissions import PermissionDTO, PermissionFilterParam, PermissionListParams, PermissionSortParam
from app.core.api.builder import ListParamsBuilder
from app.core.api.schemas import PaginatedResult
from app.core.mediators.base import BaseMediator


router = APIRouter(route_class=DishkaRoute)

list_params_builder = ListParamsBuilder(PermissionSortParam, PermissionFilterParam, PermissionListParams)



@router.post(
    "/",
    summary="Создание новое разрешение",
    description="Создает новое разрешение",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
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
    "/",
    summary="Удаление разрешения",
    description="Удаляет разрешение",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_permission(
    permission_request: PermissionDeleteRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: CurrentUserJWTData
) -> None:
    await mediator.handle_command(
        DeletePermissionCommand(
            name=permission_request.name,
            user_jwt_data=user_jwt_data
        )
    )


@router.get(
    "/",
    summary="Получить список прав",
    description="Получить список прав",
    response_model=PaginatedResult[PermissionDTO]
)
async def get_list_news(
    user_jwt_data: CurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
    params: PermissionListParams = Depends(list_params_builder),
) -> PaginatedResult[PermissionDTO]:
    list_permission = await mediator.handle_query(
        GetListPemissionsQuery(
            user_jwt_data=user_jwt_data,
            permission_query=params
        )
    )
    return list_permission
