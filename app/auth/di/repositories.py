from dishka import Provider, Scope, provide

from app.auth.repositories.user import UserRepository
from app.auth.repositories.token import TokenRepository


class AuthRepositoryProvider(Provider):
    scope = Scope.REQUEST

    user_repository = provide(UserRepository)
    token_repository = provide(TokenRepository)