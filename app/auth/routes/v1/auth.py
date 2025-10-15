# app/auth/routes/v1/auth.py

from typing import Annotated
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.commands.auth.login import LoginCommand
from app.auth.commands.auth.logout import LogoutCommand
from app.auth.commands.auth.refresh_token import RefreshTokenCommand
from app.auth.commands.users.reset_password import ResetPasswordCommand
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand
from app.auth.commands.users.send_verify import SendVerifyCommand
from app.auth.commands.users.verify import VerifyCommand
from app.auth.deps import CurrentUserJWTData
from app.auth.schemas.auth.requests import (
    ResetPasswordRequest,
    SendResetPasswordCodeRequest,
    SendVerifyCodeRequest,
    VerifyEmailRequest
)
from app.auth.schemas.auth.responses import (
    AccessTokenResponse,
)
from app.auth.schemas.token import TokenGroup
from app.core.api.rate_limiter import ConfigurableRateLimiter
from app.core.mediators.base import BaseMediator



router = APIRouter(route_class=DishkaRoute)


@router.post(
    "/login",
    summary="Вход пользователя",
    description="Аутентифицирует пользователя и возвращает пару токенов: access и refresh.",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK
)
async def login(
    mediator: FromDishka[BaseMediator],
    login_request: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    response: Response
) -> AccessTokenResponse:
    token_group: TokenGroup
    token_group, *_ = await mediator.handle_command(
        LoginCommand(
            username=login_request.username,
            password=login_request.password,
            user_agent=request.headers.get("user-agent", "")
        )
    )
    response.set_cookie(
        "refresh_token",
        token_group.refresh_token, samesite="strict",
        httponly=True, secure=True, path="/"
    )

    return AccessTokenResponse(
        access_token=token_group.access_token
    )

@router.post(
    "/refresh",
    summary="Обновление access токена",
    description="Обновляет access токен, используя refresh токен.",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK
)
async def refresh(
    mediator: FromDishka[BaseMediator],
    response: Response,
    user_jwt_data: CurrentUserJWTData,
    refresh_token: str | None = Cookie(default=None),
) -> AccessTokenResponse:
    token_group: TokenGroup
    token_group, *_ = await mediator.handle_command(
        RefreshTokenCommand(
            refresh_token=refresh_token,
            user_jwt_data=user_jwt_data
        )
    )
    response.set_cookie(
        "refresh_token",
        token_group.refresh_token, samesite="strict",
        httponly=True, secure=True, path="/"
    )

    return AccessTokenResponse(
        access_token=token_group.access_token,
    )

@router.post(
    "/logout",
    summary="Выход пользователя",
    description="Аннулирует refresh токен для выхода пользователя.",
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout(
    mediator: FromDishka[BaseMediator],
    response: Response,
    refresh_token: str | None = Cookie(default=None)
) -> None:
    await mediator.handle_command(LogoutCommand(refresh_token=refresh_token))
    response.delete_cookie("refresh_token", samesite="strict", path="/")

@router.post(
    "/send_verify_code",
    summary="Отправка кода верификации",
    description="Отправляет код для верификации email. Ограничение: 3 запроса в час.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(ConfigurableRateLimiter(times=3, seconds=60*60))],
)
async def send_verify_code(
    mediator: FromDishka[BaseMediator],
    send_verify_request: SendVerifyCodeRequest,
) -> None:
    await mediator.handle_command(
        SendVerifyCommand(email=send_verify_request.email)
    )

@router.post(
    "/send_reset_password_code",
    summary="Отправка кода сброса пароля",
    description="Отправляет код для сброса пароля. Ограничение: 3 запроса в час.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(ConfigurableRateLimiter(times=3, seconds=60*60))]
)
async def send_reset_password_code(
    mediator: FromDishka[BaseMediator],
    send_reset_password_request: SendResetPasswordCodeRequest
) -> None:
    await mediator.handle_command(
        SendResetPasswordCommand(email=send_reset_password_request.email)
    )


@router.post(
    '/verify_email',
    summary="Подтверждение email",
    description="Подтверждает email, используя переданный токен.",
    status_code=status.HTTP_204_NO_CONTENT
)
async def verify_email(
    mediator: FromDishka[BaseMediator],
    verify_email_request: VerifyEmailRequest
) -> None:
    await mediator.handle_command(VerifyCommand(token=verify_email_request.token))


@router.post(
    '/reset_password',
    summary="Сброс пароля",
    description="Сбрасывает пароль, используя токен и новые данные пароля.",
    status_code=status.HTTP_204_NO_CONTENT
)
async def reset_password(
    mediator: FromDishka[BaseMediator],
    reset_password_request: ResetPasswordRequest
) -> None:
    await mediator.handle_command(
        ResetPasswordCommand(
            token=reset_password_request.token,
            password=reset_password_request.password,
            repeat_password=reset_password_request.password_repeat
        )
    )
