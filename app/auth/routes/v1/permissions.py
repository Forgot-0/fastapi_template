from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.auth.commands.permissions.create import CreatePermissionCommand
from app.auth.commands.permissions.delete import DeletePermissionCommand
from app.auth.deps import CurrentUserJWTData
from app.auth.schemas.permission.requests import PermissionCreateRequest, PermissionDeleteRequest
from app.core.mediators.base import BaseMediator


router = APIRouter(route_class=DishkaRoute)

@router.post(
    "",
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
    "",
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