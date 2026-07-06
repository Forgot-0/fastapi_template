from dataclasses import dataclass

from app.auth.config import auth_config
from app.auth.models.user import VerifiedUserEvent
from app.core.events.event import BaseEventHandler
from app.core.message_brokers.base import BaseMessageBroker


@dataclass(frozen=True)
class PublishVerifiedUserEventHandler(BaseEventHandler[VerifiedUserEvent, None]):
    message_broker: BaseMessageBroker

    async def __call__(self, event: VerifiedUserEvent) -> None:
        await self.message_broker.send_event(
            key=str(event.user_id),
            topic=auth_config.USER_TOPIC,
            event=event
        )
