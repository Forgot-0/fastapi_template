from abc import ABC, abstractmethod

from app.core.services.auth.dto import UserJWTData


class RBACManagerInterface(ABC):
    @abstractmethod
    def is_system_user(self, jwt_data: UserJWTData) -> bool: ...

    @abstractmethod
    def check_permission(self, jwt_data: UserJWTData, permissions: set[str]) -> bool: ...
