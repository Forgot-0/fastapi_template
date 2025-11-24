from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from app.core.exceptions import FieldRequiredException
from app.core.utils import now_utc


@dataclass(frozen=True)
class BaseEvent(ABC):
    event_id: UUID = field(default_factory=uuid4, kw_only=True)
    created_at: datetime = field(default_factory=now_utc, kw_only=True)

    @classmethod
    def get_name(cls) -> str:
        name = getattr(cls, "__event_name__", None)
        if name is None:
            raise FieldRequiredException()
        return name

ET = TypeVar("ET", bound=BaseEvent)
ER = TypeVar("ER", bound=Any)


@dataclass(frozen=True)
class BaseEventHandler(ABC, Generic[ET, ER]):

    @abstractmethod
    async def __call__(self, event: ET) -> ER: ...


@dataclass
class EventRegisty:
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
