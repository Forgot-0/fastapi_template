from dishka import Provider, Scope, provide

from app.auth.services.tokens import AuthService
from app.auth.services.users import UserService


class AuthServiceProvider(Provider):
    scope = Scope.REQUEST

    user_service = provide(UserService)
    token_service = provide(AuthService)
