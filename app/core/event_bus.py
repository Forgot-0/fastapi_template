from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Type

from app.core.event import ER, ET, BaseEvent, BaseEventHandler


@dataclass(eq=False)
class EventBus:
    events_map: dict[Type[BaseEvent], list[BaseEventHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    def subscribe(self, event: Type[BaseEvent], event_handlers: Iterable[BaseEventHandler[ET, ER]]):
        self.events_map[event].extend(event_handlers)

    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        result = []

        for event in events:
            handlers = self.events_map.get(event.__class__)
            if not handlers:
                raise 
            result.extend([await handler.handle(event) for handler in handlers])

        return result