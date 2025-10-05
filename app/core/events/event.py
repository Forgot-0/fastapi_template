from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Type, TypeVar
from uuid import UUID, uuid4

from app.core.utils import now_utc




@dataclass(frozen=True)
class BaseEvent(ABC):
    event_id: UUID = field(default_factory=uuid4, kw_only=True)
    created_at: datetime = field(default_factory=now_utc, kw_only=True)

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
    async def __call__(self, event: ET) -> ER: ...


@dataclass
class EventRegisty:
    events_map: dict[Type[BaseEvent], list[Type[BaseEventHandler]]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    def subscribe(self, event: Type[BaseEvent], type_handlers: Iterable[Type[BaseEventHandler]]) -> None:
        self.events_map[event].extend(type_handlers)

    def get_handler_types(self, events: Iterable[BaseEvent]) -> Iterable[Type[BaseEventHandler]]:
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