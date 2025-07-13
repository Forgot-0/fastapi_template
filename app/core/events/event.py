from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4


@dataclass(frozen=True)
class BaseEvent(ABC):
    event_id: UUID = field(default_factory=uuid4, kw_only=True)
    created_at: datetime = field(default_factory=datetime.now, kw_only=True)

    @classmethod
    def get_name(cls) -> str:
        name = getattr(cls, '__event_name__', None)
        if name is None:
            raise 
        return name

ET = TypeVar('ET', bound=BaseEvent)
ER = TypeVar('ER', bound=Any)


@dataclass(frozen=True)
class BaseEventHandler(ABC, Generic[ET, ER]):

    @abstractmethod
    async def handle(self, event: ET) -> ER:
        ...


# @dataclass(frozen=True)
# class PublisherEventHandler(BaseEventHandler[BaseEvent, None]):
#     message_broker: BaseMessageBroker
#     broker_topic: str | None = 'example'

#     async def handle(self, event: BaseEvent) -> None:
#         await self.message_broker.send_message(
#             topic=self.broker_topic,
#             value=convert_event_to_broker_message(event=event),
#             key=str(event.event_id).encode(),
#         )