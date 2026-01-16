from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, status

from app.auth.commands.roles.add_permissions import AddPermissionRoleCommand
from app.auth.commands.roles.create import CreateRoleCommand
from app.auth.commands.roles.delete_permissions import DeletePermissionRoleCommand
from app.auth.deps import AuthCurrentUserJWTData
from app.auth.dtos.role import RoleDTO
from app.auth.exceptions import (
    AccessDeniedException,
    DuplicateRoleException,
    InvalidRoleNameException,
    NotFoundPermissionsException,
    NotFoundRoleException,
    ProtectedPermissionException,
)
from app.auth.queries.roles.get_list import GetListRolesQuery
from app.auth.schemas.roles.requests import GetRolesRequest, RoleCreateRequest, RolePermissionRequest
from app.core.api.builder import create_response
from app.core.db.repository import PageResult
from app.core.mediators.base import BaseMediator

router = APIRouter(route_class=DishkaRoute)



@router.post(
    "/",
    summary="Creating a new role",
    description="Creates a new role with permissions",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: create_response(InvalidRoleNameException(name="string")),
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response(NotFoundPermissionsException(missing={"string" })),
        409: create_response([
            DuplicateRoleException(name="string"), ProtectedPermissionException(name="string")
        ])
    }
)
async def create_role(
    role_request: RoleCreateRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: AuthCurrentUserJWTData
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

@router.get(
    "/",
    summary="Get a list of roles",
    description="Get a list of roles",
    responses={
        403: create_response(AccessDeniedException(need_permissions={"string" })),
    }
)
async def get_list_news(
    user_jwt_data: AuthCurrentUserJWTData,
    mediator: FromDishka[BaseMediator],
    params: GetRolesRequest=Query(),
) -> PageResult[RoleDTO]:
    list_role: PageResult[RoleDTO]
    list_role = await mediator.handle_query(
        GetListRolesQuery(
            user_jwt_data=user_jwt_data,
            role_filter=params.to_role_filter()
        )
    )
    return list_role


@router.post(
    "/{role_name}/permissions",
    summary="Adding role permissions",
    description="Adding role permissions",
    response_model=None,
    status_code=status.HTTP_200_OK,
    responses={
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response([
            NotFoundRoleException(name="string"), NotFoundPermissionsException(missing={"string"})
        ])
    }
)
async def add_permission_role(
    role_name: str,
    role_request: RolePermissionRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: AuthCurrentUserJWTData
) -> None:
    await mediator.handle_command(
        AddPermissionRoleCommand(
            role_name=role_name,
            permissions=role_request.permission,
            user_jwt_data=user_jwt_data
        )
    )


@router.delete(
    "/{role_name}/permissions",
    summary="Removes permissions from a role",
    description="Removes permissions from a role",
    response_model=None,
    status_code=status.HTTP_200_OK,
    responses={
        403: create_response(AccessDeniedException(need_permissions={"string" })),
        404: create_response([
            NotFoundRoleException(name="string"), NotFoundPermissionsException(missing={"string"})
        ])
    }
)
async def delete_permission_role(
    role_name: str,
    role_request: RolePermissionRequest,
    mediator: FromDishka[BaseMediator],
    user_jwt_data: AuthCurrentUserJWTData
) -> None:
    await mediator.handle_command(
        DeletePermissionRoleCommand(
            role_name=role_name,
            permissions=role_request.permission,
            user_jwt_data=user_jwt_data
        )
    )

