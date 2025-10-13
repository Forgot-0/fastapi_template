from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.auth.commands.roles.add_permissions import AddPermissionRoleCommand
from app.auth.commands.roles.assign_role_to_user import AssignRoleCommand
from app.auth.commands.roles.create import CreateRoleCommand
from app.auth.commands.roles.delete_permissions import DeletePermissionRoleCommand
from app.auth.deps import CurrentUserJWTData
from app.auth.schemas.roles.requests import RoleAssignRequest, RoleCreateRequest, RolePermissionRequest
from app.core.mediators.base import BaseMediator


router = APIRouter(route_class=DishkaRoute)


@router.post(
    "",
    summary="Создание новой роли",
    description="Создает новую роль с правами",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    role_request: RoleCreateRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: CurrentUserJWTData
) -> None:
    await mediator.handle_command(
        CreateRoleCommand(
            user_jwt_data=user_jwt_data,
            role_name=role_request.name,
            description=role_request.description,
            security_level=role_request.security_level,
            permissions=role_request.permissions
        )
    )


@router.post(
    "/assign/{user_id}",
    summary="Добавление роли пользователю",
    description="Добавление роли пользователю",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def assign_role(
    user_id: int,
    role_request: RoleAssignRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: CurrentUserJWTData
) -> None:
    await mediator.handle_command(
        AssignRoleCommand(
            assign_to_user=user_id,
            role_name=role_request.role_name,
            user_jwt_data=user_jwt_data
        )
    )


@router.post(
    "{role_name}/add_permission",
    summary="Добавления прав роли",
    description="Добавления прав роли",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def add_permission_role(
    role_name: str,
    role_request: RolePermissionRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: CurrentUserJWTData
) -> None:
    await mediator.handle_command(
        AddPermissionRoleCommand(
            role_name=role_name,
            permissions=role_request.permission,
            user_jwt_data=user_jwt_data
        )
    )


@router.post(
    "{role_name}/delete_permission",
    summary="Удаляет права в роли",
    description="Удаляет права в роли",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def delete_permission_role(
    role_name: str,
    role_request: RolePermissionRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: CurrentUserJWTData
) -> None:
    await mediator.handle_command(
        DeletePermissionRoleCommand(
            role_name=role_name,
            permissions=role_request.permission,
            user_jwt_data=user_jwt_data
        )
    )

