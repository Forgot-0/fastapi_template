from dataclasses import dataclass

from app.auth.models.user import CreatedUserEvent
from app.auth.services.users import UserService
from app.core.events.event import BaseEventHandler



@dataclass(frozen=True)
class SendVerifyEventHandler(BaseEventHandler[CreatedUserEvent, None]):
    user_service: UserService

    async def __call__(self, event: CreatedUserEvent) -> None:
        await self.user_service.send_verify(email=event.email)