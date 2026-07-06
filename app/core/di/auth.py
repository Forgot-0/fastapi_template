from dishka import Provider, Scope, provide

from app.core.services.auth.jwt_manager import JWTManager
from app.core.services.auth.rbac import RBACManager


class AuthServicesProvider(Provider):
    scope = Scope.APP


    @provide
    def get_jwt_manager(self) -> JWTManager:
        return JWTManager()

    @provide
    def get_rbac_manager(self) -> RBACManager:
        return RBACManager()

