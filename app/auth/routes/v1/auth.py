# app/auth/routes/v1/auth.py

from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.commands.auth.login import LoginCommand
from app.auth.commands.auth.logout import LogoutCommand
from app.auth.commands.auth.refresh_token import RefreshTokenCommand
from app.auth.commands.users.reset_password import ResetPasswordCommand
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand
from app.auth.commands.users.send_verify import SendVerifyCommand
from app.auth.commands.users.verify import VerifyCommand
from app.auth.deps import Mediator
from app.auth.schemas.auth.requests import (
    LogoutRequest,
    ResetPasswordRequest,
    SendResetPasswordCodeRequest,
    SendVerifyCodeRequest,
    RefreshTokenRequest,
    VerifyEmailRequest
)
from app.auth.schemas.auth.responses import (
    AccessTokenResponse,
    TokenResponse,
)
from app.auth.schemas.token import TokenGroup
from app.core.api.rate_limeter import ConfigurableRateLimiter

router = APIRouter()

@router.post(
    "/login",
    summary="Вход пользователя",
    description="Аутентифицирует пользователя и возвращает пару токенов: access и refresh.",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def login(
    mediator: Mediator,
    login_request: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> TokenResponse:
    response: TokenGroup = await mediator.handle_command(
        LoginCommand(
            username=login_request.username,
            password=login_request.password
        )
    )
    return TokenResponse(
        access_token=response.access_token,
        refresh_token=response.refresh_token
    )

@router.post(
    "/refresh",
    summary="Обновление access токена",
    description="Обновляет access токен, используя refresh токен.",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK
)
async def refresh(
    mediator: Mediator,
    refresh_request: RefreshTokenRequest,
) -> AccessTokenResponse:
    access_token: str = await mediator.handle_command(
        RefreshTokenCommand(refresh_token=refresh_request.refresh_token)
    )
    return AccessTokenResponse(access_token=access_token)

@router.post(
    "/logout",
    summary="Выход пользователя",
    description="Аннулирует refresh токен для выхода пользователя.",
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout(
    mediator: Mediator,
    logout_request: LogoutRequest
) -> None:
    await mediator.handle_command(LogoutCommand(refresh_token=logout_request.refresh_token))

@router.post(
    "/send_verify_code",
    summary="Отправка кода верификации",
    description="Отправляет код для верификации email. Ограничение: 3 запроса в час.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            ConfigurableRateLimiter(
                times=3, seconds=60*60, identifier=ConfigurableRateLimiter.get_identifier_by_body
            )
        )
    ],
)
async def send_verify_code(
    mediator: Mediator,
    send_verify_request: SendVerifyCodeRequest
) -> None:
    await mediator.handle_command(
        SendVerifyCommand(email=send_verify_request.email)
    )

@router.post(
    "/send_reset_password_code",
    summary="Отправка кода сброса пароля",
    description="Отправляет код для сброса пароля. Ограничение: 3 запроса в час.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            ConfigurableRateLimiter(
                times=3, seconds=60*60, identifier=ConfigurableRateLimiter.get_identifier_by_body
            )
        )
    ],
)
async def send_reset_password_code(
    mediator: Mediator,
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
    mediator: Mediator,
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
    mediator: Mediator,
    reset_password_request: ResetPasswordRequest
) -> None:
    await mediator.handle_command(
        ResetPasswordCommand(
            token=reset_password_request.token,
            password=reset_password_request.password,
            repeat_password=reset_password_request.password_repeat
        )
    )
