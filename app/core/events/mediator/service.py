from collections.abc import Iterable
from dataclasses import dataclass

from dishka import AsyncContainer


from app.core.events.event import ER, BaseEvent
from app.core.events.service import BaseEventBus
from app.core.exceptions import NotHandlerRegistry




@dataclass(eq=False)
class MediatorEventBus(BaseEventBus):
    container: AsyncContainer

    async def publish(self, events: Iterable[BaseEvent]) -> None:
        for event in events:
            type_handlers = self.event_registy.get_handler_types([event])
            if not type_handlers:
                continue

            for type_handler in type_handlers:
                async with self.container() as requests_container:
                    handler = await requests_container.get(type_handler)
                    await handler(event)

