from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Optional, Type, TypeVar
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

@dataclass
class EventHandleRegistry:
    handler_type: Type[BaseEventHandler]
    instance: Optional[BaseEventHandler] = None


@dataclass
class EventRegisty:
    events_map: dict[Type[BaseEvent], list[EventHandleRegistry]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    def subscribe(self, event: Type[BaseEvent], type_handlers: Iterable[EventHandleRegistry]) -> None:
        self.events_map[event].extend(type_handlers)

    def get_handler_types(self, events: Iterable[BaseEvent]) -> Iterable[EventHandleRegistry]:
        handler_types = []
        for event in events:
            handler_types.extend(self.events_map.get(event.__class__, []))
        return handler_types


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