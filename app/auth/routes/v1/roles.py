from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.auth.commands.roles.create import CreateRoleCommand
from app.auth.deps import CurrentUserJWTData
from app.auth.schemas.roles.requests import RoleCreateRequest
from app.core.mediators.base import BaseMediator


router = APIRouter(route_class=DishkaRoute)


@router.post(
    "",
    summary="Создание новой роли",
    description="Создает новую роль с правами",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def create_role(
    role_requests: RoleCreateRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: CurrentUserJWTData
) -> None:
    await mediator.handle_command(
        CreateRoleCommand(
            user_jwt_data=user_jwt_data,
            role_name=role_requests.name,
            description=role_requests.description,
            security_level=role_requests.security_level,
            permissions=role_requests.permissions
        )
    )


