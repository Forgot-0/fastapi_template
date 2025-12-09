# app/auth/routes/v1/auth.py

from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.commands.auth.auth_url import CreateOAuthAuthorizeUrlCommand
from app.auth.commands.auth.login import LoginCommand
from app.auth.commands.auth.logout import LogoutCommand
from app.auth.commands.auth.oauth import (
    ProcessOAuthCallbackCommand,
)
from app.auth.commands.auth.refresh_token import RefreshTokenCommand
from app.auth.commands.users.reset_password import ResetPasswordCommand
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand
from app.auth.commands.users.send_verify import SendVerifyCommand
from app.auth.commands.users.verify import VerifyCommand
from app.auth.deps import CurrentUserJWTData, CurrentUserModel
from app.auth.exceptions import (
    ExpiredTokenException,
    InvalidTokenException,
    LinkedAnotherUserOAuthException,
    NotExistProviderOAuthException,
    NotFoundOrInactiveSessionException,
    NotFoundUserException,
    OAuthStateNotFoundException,
    PasswordMismatchException,
    WrongLoginDataException,
)
from app.auth.schemas.auth.requests import (
    OAuthCallbackQuery,
    ResetPasswordRequest,
    SendResetPasswordCodeRequest,
    SendVerifyCodeRequest,
    VerifyEmailRequest,
)
from app.auth.schemas.auth.responses import (
    AccessTokenResponse,
)
from app.auth.schemas.tokens import TokenGroup
from app.auth.services.cookie_manager import RefreshTokenCookieManager
from app.core.api.builder import create_response
from app.core.api.rate_limiter import ConfigurableRateLimiter
from app.core.mediators.base import BaseMediator

router = APIRouter(route_class=DishkaRoute)


@router.post(
    "/login",
    summary="User login",
    description="Authenticates the user and returns a pair of tokens: access and refresh.",
    status_code=status.HTTP_200_OK,
    responses={
        400: create_response(WrongLoginDataException(username="aboba"))
    }
)
async def login(
    mediator: FromDishka[BaseMediator],
    refresh_cookie_manager: FromDishka[RefreshTokenCookieManager],
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
    refresh_cookie_manager.set_refresh_token(response, token_group.refresh_token)
    return AccessTokenResponse(
        access_token=token_group.access_token
    )

@router.post(
    "/refresh",
    summary="Refreshing the access token",
    description="Refreshes the access token using the refresh token.",
    status_code=status.HTTP_200_OK,
    responses={
        400: create_response([InvalidTokenException(), ExpiredTokenException()]),
        404: create_response(NotFoundOrInactiveSessionException())
    },
    dependencies=[Depends(ConfigurableRateLimiter(times=4, seconds=5*60))]
)
async def refresh(
    mediator: FromDishka[BaseMediator],
    refresh_cookie_manager: FromDishka[RefreshTokenCookieManager],
    response: Response,
    user_jwt_data: CurrentUserJWTData,
    refresh_token: Annotated[str | None, Cookie()] = None ,
) -> AccessTokenResponse:
    token_group: TokenGroup
    token_group, *_ = await mediator.handle_command(
        RefreshTokenCommand(
            refresh_token=refresh_token,
            user_jwt_data=user_jwt_data
        )
    )
    refresh_cookie_manager.set_refresh_token(response, token_group.refresh_token)

    return AccessTokenResponse(
        access_token=token_group.access_token,
    )

@router.post(
    "/logout",
    summary="User logout",
    description="Invalidates the user's refresh token to log out.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: create_response(InvalidTokenException())
    }
)
async def logout(
    mediator: FromDishka[BaseMediator],
    refresh_cookie_manager: FromDishka[RefreshTokenCookieManager],
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None
) -> None:
    await mediator.handle_command(LogoutCommand(refresh_token=refresh_token))
    refresh_cookie_manager.delete_refresh_token(response)

@router.post(
    "/verifications/email",
    summary="Sending a verification code",
    description="Sends an email verification code. Limit: 3 requests per hour.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: create_response(NotFoundUserException(user_by="test@test.com", user_field="email"))
    },
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
    "/password-resets",
    summary="Sending a password reset code",
    description="Sends a password reset code. Limit: 3 requests per hour.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: create_response(NotFoundUserException(user_by="test@test.com", user_field="email"))
    },
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
    "/verifications/email/verify",
    summary="Email confirmation",
    description="Confirms the email using the passed token.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: create_response(InvalidTokenException()),
        404: create_response(NotFoundUserException(user_by=1, user_field="id"))
    },
    dependencies=[Depends(ConfigurableRateLimiter(times=3, seconds=60*60))]
)
async def verify_email(
    mediator: FromDishka[BaseMediator],
    verify_email_request: VerifyEmailRequest
) -> None:
    await mediator.handle_command(VerifyCommand(token=verify_email_request.token))


@router.post(
    "/password-resets/confirm",
    summary="Reset password",
    description="Resets the password using the token and new password data.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: create_response([InvalidTokenException(), PasswordMismatchException()]),
        404: create_response(NotFoundUserException(user_by=1, user_field="id"))
    },
    dependencies=[Depends(ConfigurableRateLimiter(times=3, seconds=60*60))]
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


@router.get(
    "/oauth/{provider}/authorize",
    summary="Get URL for OAuth authorization",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    responses={
        400: create_response(NotExistProviderOAuthException(provider="test"))
    }
)
async def oauth_authorize(
    mediator: FromDishka[BaseMediator],
    provider: str,
) -> RedirectResponse:
    url: str
    url, *_ = await mediator.handle_command(
        CreateOAuthAuthorizeUrlCommand(provider=provider, user_id=None)
    )

    return RedirectResponse(url=url)


@router.get(
    "/oauth/{provider}/authorize/connect",
    summary="Get the OAuth connection URL for an existing user",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    responses={
        400: create_response(NotExistProviderOAuthException(provider="test"))
    }
)
async def oauth_authorize_connect(
    mediator: FromDishka[BaseMediator],
    provider: str,
    current_user: CurrentUserModel,
) -> RedirectResponse:
    url: str
    url, *_ = await mediator.handle_command(
        CreateOAuthAuthorizeUrlCommand(provider=provider, user_id=current_user.id)
    )
    return RedirectResponse(url=url)


@router.get(
    "/oauth/{provider}/callback",
    summary="Callback for OAuth provider",
    status_code=status.HTTP_200_OK,
    responses={
        400: create_response(NotExistProviderOAuthException(provider="string")),
        404: create_response(
            [
                OAuthStateNotFoundException(state="string"),
                NotFoundUserException(user_by=1, user_field="id"),
            ]
        ),
        409: create_response(LinkedAnotherUserOAuthException(provider="string"))
    }
)
async def oauth_callback(
    mediator: FromDishka[BaseMediator],
    refresh_cookie_manager: FromDishka[RefreshTokenCookieManager],
    oauth_callback_query: OAuthCallbackQuery,
    request: Request,
    response: Response,
) -> AccessTokenResponse:
    token_group: TokenGroup
    token_group, *_ = await mediator.handle_command(
        ProcessOAuthCallbackCommand(
            provider=oauth_callback_query.provider,
            code=oauth_callback_query.code,
            state=oauth_callback_query.state,
            user_agent=request.headers.get("user-agent", ""),
        )
    )
    refresh_cookie_manager.set_refresh_token(response, token_group.refresh_token)
    return AccessTokenResponse(access_token=token_group.access_token)

