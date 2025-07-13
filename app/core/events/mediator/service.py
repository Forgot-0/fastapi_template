from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Callable, Type

from app.core.events.event import ER, ET, BaseEvent, BaseEventHandler
from app.core.events.service import BaseEventBus



@dataclass(eq=False)
class MediatorEventBus(BaseEventBus):
    events_map: dict[Type[BaseEvent], list[BaseEventHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    def __call__(self, event: Type[BaseEvent]) -> Callable[..., BaseEventHandler[ET, ER]]:
        def decorator(func: BaseEventHandler[ET, ER]) -> BaseEventHandler[ET, ER]:
            self.subscribe(event=event, event_handlers=[func])
            return func
        return decorator

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
