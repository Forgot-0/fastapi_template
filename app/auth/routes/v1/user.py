# app/auth/routes/v1/user.py

from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status

from app.auth.commands.permissions.add_permission_user import AddPermissionToUserCommand
from app.auth.commands.permissions.remove_permission_user import DeletePermissionToUserCommand
from app.auth.commands.roles.assign_role_to_user import AssignRoleCommand
from app.auth.commands.roles.remove_role_user import RemoveRoleCommand
from app.auth.commands.users.register import RegisterCommand
from app.auth.deps import ActiveUserModel, CurrentUserJWTData
from app.auth.exceptions import (
    AccessDeniedException,
    DuplicateUserException,
    InvalidTokenException,
    NotFoundPermissionsException,
    NotFoundRoleException,
    NotFoundUserException,
    PasswordMismatchException,
)
from app.auth.queries.sessions.get_list_by_user import GetListSessionsUserQuery
from app.auth.queries.users.get_list import GetListUserQuery
from app.auth.schemas.roles.requests import RoleAssignRequest
from app.auth.schemas.sessions import SessionDTO, SessionFilterParam, SessionListParams, SessionSortParam
from app.auth.schemas.user import UserDTO, UserFilterParam, UserListParams, UserSortParam
from app.auth.schemas.users.requests import UserCreateRequest, UserPermissionRequest
from app.auth.schemas.users.responses import UserResponse
from app.core.api.builder import ListParamsBuilder, create_response
from app.core.api.schemas import PaginatedResult
from app.core.mediators.base import BaseMediator

router = APIRouter(route_class=DishkaRoute)

user_list_params_builder = ListParamsBuilder(UserSortParam, UserFilterParam, UserListParams)
session_list_params_builder = ListParamsBuilder(SessionSortParam, SessionFilterParam, SessionListParams)



@router.post(
    "/register",
    summary="",
    description="",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: create_response(PasswordMismatchException()),
        409: create_response(DuplicateUserException(field="string", value="string"))
    }
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
    responses={
        400: create_response(InvalidTokenException()),
        403: create_response(AccessDeniedException(need_permissions={"user:active" })),
        404: create_response(NotFoundUserException(user_by=1, user_field="id"))
    }
)
async def me(user: ActiveUserModel) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email
    )

@router.post(
    "/{user_id}/roles",
    summary="Adding a role to a user",
    description="Adding a role to a user",
    status_code=status.HTTP_200_OK,
    responses={
        400: create_response(InvalidTokenException()),
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response(
            [NotFoundRoleException(name="strig"), NotFoundUserException(user_by=1, user_field="id")]
        )
    }
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
    summary="Removing a role from a user",
    description="Removing a role from a user",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: create_response(InvalidTokenException()),
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response(
            [NotFoundRoleException(name="strig"), NotFoundUserException(user_by=1, user_field="id")]
        )
    }
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
    summary="Adding permissions to a user",
    description="Adding permissions to a user",
    status_code=status.HTTP_200_OK,
    responses={
        400: create_response(InvalidTokenException()),
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response(
            [
                NotFoundPermissionsException(missing={"string" }),
                NotFoundUserException(user_by=1, user_field="id")
            ]
        )
    }
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
    summary="Removing user permissions",
    description="Removing user permissions",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: create_response(InvalidTokenException()),
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response(
            [
                NotFoundPermissionsException(missing={"string" }),
                NotFoundUserException(user_by=1, user_field="id")
            ]
        )
    }
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
    summary="Get a list of users",
    description="Get a list of users",
    status_code=status.HTTP_200_OK,
    responses={
        400: create_response(InvalidTokenException()),
        403: create_response(AccessDeniedException(need_permissions={"string" })),
    }
)
async def get_list_user(
    user_jwt_data: CurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
    params: Annotated[UserListParams, Depends(user_list_params_builder)],
) -> PaginatedResult[ActiveUserModel]:
    list_user: PaginatedResult[UserDTO]
    list_user = await mediator.handle_query(
        GetListUserQuery(
            user_jwt_data=user_jwt_data,
            user_query=params
        )
    )
    return list_user


@router.get(
    "/sessions",
    summary="Get active user sessions",
    description="Get active user sessions",
    status_code=status.HTTP_200_OK,
    responses={
        400: create_response(InvalidTokenException()),
    }
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

