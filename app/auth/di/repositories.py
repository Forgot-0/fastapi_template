from dishka import Provider, Scope, provide

from app.auth.repositories.user import UserRepository
from app.auth.repositories.token import TokenRepository


class AuthRepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def user_repository(self) -> UserRepository:
        return UserRepository()

    @provide
    def token_repository(self) -> TokenRepository:
        return TokenRepository()