# app/auth/routes/v1/oauth.py

from typing import Annotated
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Request, Response, status, HTTPException

from app.auth.commands.auth.oauth_connect import OAuthConnectCommand
from app.auth.commands.auth.oauth_login import OAuthLoginCommand

from app.auth.deps import CurrentUserJWTData
from app.auth.schemas.auth.responses import AccessTokenResponse, OAuthUrlResponse
from app.auth.schemas.oauth import OAuthLoginRequest, OAuthConnectRequest
from app.auth.schemas.token import TokenGroup
from app.auth.services.oauth_manager import OAuthManager
from app.core.mediators.base import BaseMediator


router = APIRouter(route_class=DishkaRoute)


@router.get(
    "/{provider}/authorize",
    summary="Получить URL-адрес авторизации OAuth",
    description="Возвращает URL авторизации для указанного провайдера OAuth (google, yandex, github)",
    response_model=OAuthUrlResponse,
    status_code=status.HTTP_200_OK,
)
async def get_oauth_url(
    oauth_manager: FromDishka[OAuthManager],
    provider: str,
) -> OAuthUrlResponse:

    oauth_provider = oauth_manager.oauth_provider.get_provider(provider)
    auth_url = oauth_provider.get_auth_url()
    return OAuthUrlResponse(url=auth_url)

@router.post(
    "/login",
    summary="OAuth Login",
    description="Login у провайдера OAuth, используя код авторизации",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK
)
async def oauth_login(
    mediator: FromDishka[BaseMediator],
    oauth_request: OAuthLoginRequest,
    request: Request,
    response: Response
) -> AccessTokenResponse:
    token_group: TokenGroup
    token_group, *_ = await mediator.handle_command(
        OAuthLoginCommand(
            code=oauth_request.code,
            provider=oauth_request.provider,
            user_agent=request.headers.get("user-agent", "")
        )
    )
    response.set_cookie(
        "refresh_token",
        token_group.refresh_token,
        samesite="strict",
        httponly=True,
        secure=True,
        path="/"
    )
    return AccessTokenResponse(access_token=token_group.access_token)


@router.post(
    "/connect",
    summary="Подключите учетную запись OAuth к существующему пользователю",
    description="Подключите учетную запись OAuth к аутентифицированному пользователю.",
    status_code=status.HTTP_200_OK
)
async def oauth_connect(
    mediator: FromDishka[BaseMediator],
    oauth_request: OAuthConnectRequest,
    user_jwt_data: CurrentUserJWTData,
    request: Request
) -> None:
    await mediator.handle_command(
        OAuthConnectCommand(
            code=oauth_request.code,
            provider=oauth_request.provider,
            user_id=int(user_jwt_data.id),
            user_agent=request.headers.get("user-agent", "")
        )
    )
