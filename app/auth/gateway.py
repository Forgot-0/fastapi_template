from abc import ABC, abstractmethod

from app.auth.schemas.user import UserDTO


class BaseAuthGateway(ABC):

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserDTO:
        ...

