from dishka import Provider, provide, Scope

from app.auth.repositories.user import UserRepository
from app.auth.repositories.token import TokenRepository


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_repository(self) -> UserRepository:
        return UserRepository()
    
    @provide
    def get_token_repository(self) -> TokenRepository:
        return TokenRepository()