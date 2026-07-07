from dishka import Provider, Scope, provide

from app.core.services.auth.jwt_manager import JWTManager


class AuthServicesProvider(Provider):
    scope = Scope.APP

    @provide
    def get_jwt_manager(self) -> JWTManager:
        return JWTManager()

