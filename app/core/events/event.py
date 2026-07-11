from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from app.core.exceptions import FieldRequiredError
from app.core.utils import now_utc


@dataclass(frozen=True)
class BaseEvent(ABC):
    event_id: UUID = field(default_factory=uuid4, kw_only=True)
    created_at: datetime = field(default_factory=now_utc, kw_only=True)

    @classmethod
    def get_name(cls) -> str:
        name = getattr(cls, "__event_name__", None)
        if name is None:
            raise FieldRequiredError
        return name

    @abstractmethod
    def get_partition_key(self) -> str:
        ...

@dataclass(frozen=True)
class BaseEventHandler[ET: BaseEvent, ER: Any](ABC):

    @abstractmethod
    async def __call__(self, event: ET) -> ER: ...


@dataclass
class EventRegistry:
    events_map: dict[type[BaseEvent], list[type[BaseEventHandler]]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    def subscribe(self, event: type[BaseEvent], type_handlers: Iterable[type[BaseEventHandler]]) -> None:
        self.events_map[event].extend(type_handlers)

    def get_handler_types(self, events: Iterable[BaseEvent]) -> Iterable[type[BaseEventHandler]]:
        handler_types = []
        for event in events:
            handler_types.extend(self.events_map.get(event.__class__, []))
        return handler_types
