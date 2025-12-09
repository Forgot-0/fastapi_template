from collections.abc import Iterable
from dataclasses import dataclass

from dishka import AsyncContainer

from app.core.events.event import BaseEvent
from app.core.events.service import BaseEventBus


@dataclass(eq=False)
class MediatorEventBus(BaseEventBus):
    container: AsyncContainer

    async def publish(self, events: Iterable[BaseEvent]) -> None:
        for event in events:
            type_handlers = self.event_registy.get_handler_types([event])
            if not type_handlers:
                continue

            async with self.container() as requests_container:
                for type_handler in type_handlers:
                        handler = await requests_container.get(type_handler)
                        await handler(event)
