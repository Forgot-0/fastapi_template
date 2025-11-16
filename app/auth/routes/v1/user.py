# app/auth/routes/v1/user.py

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Response, status
from app.auth.commands.permissions.add_permission_user import AddPermissionToUserCommand
from app.auth.commands.permissions.remove_permission_user import DeletePermissionToUserCommand
from app.auth.commands.roles.assign_role_to_user import AssignRoleCommand
from app.auth.commands.roles.remove_role_user import RemoveRoleCommand
from app.auth.commands.users.register import RegisterCommand
from app.auth.deps import ActiveUserModel, CurrentUserJWTData
from app.auth.queries.sessions.get_list_by_user import GetListSessionsUserQuery
from app.auth.queries.users.get_list import GetListUserQuery
from app.auth.schemas.roles.requests import RoleAssignRequest
from app.auth.schemas.sessions import SessionDTO, SessionFilterParam, SessionListParams, SessionSortParam
from app.auth.schemas.user import UserDTO, UserFilterParam, UserListParams, UserSortParam
from app.auth.schemas.users.requests import UserCreateRequest, UserPermissionRequest
from app.auth.schemas.users.responses import UserResponse
from app.core.api.builder import ListParamsBuilder
from app.core.api.schemas import PaginatedResult
from app.core.mediators.base import BaseMediator


router = APIRouter(route_class=DishkaRoute)

user_list_params_builder = ListParamsBuilder(UserSortParam, UserFilterParam, UserListParams)
session_list_params_builder = ListParamsBuilder(SessionSortParam, SessionFilterParam, SessionListParams)



@router.post(
    "/register",
    summary="",
    description="",
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    mediator: FromDishka[BaseMediator],
    user_request: UserCreateRequest
) -> UserResponse:
    user: UserDTO
    user, *_ = await mediator.handle_command(
        RegisterCommand(
            username=user_request.username,
            email=user_request.email,
            password=user_request.password,
            password_repeat=user_request.password_repeat
        )
    )
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email
    )

@router.get(
    "/me",
    summary="",
    description="",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def me(user: ActiveUserModel) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email
    )

@router.post(
    "/{user_id}/roles",
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

@router.delete(
    "/{user_id}/roles/{role_name}",
    summary="Удаление роли пользователю",
    description="Удаление роли пользователю",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_role(
    user_id: int,
    role_name: str,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: CurrentUserJWTData
) -> None:
    await mediator.handle_command(
        RemoveRoleCommand(
            remove_from_user=user_id,
            role_name=role_name,
            user_jwt_data=user_jwt_data
        )
    )

@router.post(
    "/{user_id}/permissions",
    summary="Добавление прав пользователю",
    description="Добавление прав пользователю",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def add_permissions_to_user(
    user_id: int,
    permissions_request: UserPermissionRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: CurrentUserJWTData
) -> None:
    await mediator.handle_command(
        AddPermissionToUserCommand(
            user_id=user_id,
            permissions=permissions_request.permissions,
            user_jwt_data=user_jwt_data
        )
    )

@router.delete(
    "/{user_id}/permissions",
    summary="удаление прав пользователю",
    description="удаление прав пользователю",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_permissions_to_user(
    user_id: int,
    permissions_request: UserPermissionRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: CurrentUserJWTData
) -> None:
    await mediator.handle_command(
        DeletePermissionToUserCommand(
            user_id=user_id,
            permissions=permissions_request.permissions,
            user_jwt_data=user_jwt_data
        )
    )


@router.get(
    "/",
    summary="Получить список пользователей",
    description="Получить список пользователей",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResult[UserDTO]
)
async def get_list_user(
    user_jwt_data: CurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
    params: UserListParams = Depends(user_list_params_builder),
) -> PaginatedResult[UserDTO]:
    list_user = await mediator.handle_query(
        GetListUserQuery(
            user_jwt_data=user_jwt_data,
            user_query=params
        )
    )
    return list_user


@router.get(
    "/sessions",
    summary="Получить активные сессии пользователя",
    description="Получить активные сессии пользователя",
    status_code=status.HTTP_200_OK,
    response_model=list[SessionDTO]
)
async def get_list_user_session(
    user_jwt_data: CurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
) -> list[SessionDTO]:
    return await mediator.handle_query(
        GetListSessionsUserQuery(
            user_jwt_data=user_jwt_data
        )
    )

