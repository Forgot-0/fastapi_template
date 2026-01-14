from dishka import Provider, Scope, provide

from app.core.configs.app import app_config
from app.core.services.auth.jwt_manager import JWTManager
from app.core.services.auth.rbac import RBACManager


class AuthServicesProvider(Provider):
    scope = Scope.APP

    @provide
    def get_jwt_manager(self) -> JWTManager:
        return JWTManager(
            jwt_secret=app_config.JWT_SECRET_KEY,
            jwt_algorithm=app_config.JWT_ALGORITHM
        )

    @provide
    def get_rbac_manager(self) -> RBACManager:
        return RBACManager()

