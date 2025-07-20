# app/auth/routes/v1/user.py

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status
from app.auth.commands.users.register import RegisterCommand
from app.auth.deps import ActiveUserModel
from app.auth.schemas.user import UserDTO
from app.auth.schemas.users.requests import UserCreateRequest
from app.auth.schemas.users.responses import UserResponse
from app.core.mediators.base import BaseMediator


router = APIRouter(route_class=DishkaRoute)


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
    status_code=status.HTTP_200_OK
)
async def me(user: ActiveUserModel) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email
    )