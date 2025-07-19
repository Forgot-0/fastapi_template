from collections.abc import Iterable
from dataclasses import dataclass

from dishka import AsyncContainer


from app.core.events.event import ER, BaseEvent
from app.core.events.service import BaseEventBus




@dataclass(eq=False)
class MediatorEventBus(BaseEventBus):
    container: AsyncContainer

    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        result = []

        for event in events:
            type_handlers = self.event_registy.get_handler_types([event])
            if not type_handlers:
                raise 

            for type_handler in type_handlers:
                if type_handler.instance:
                    result.append(await type_handler.instance.handle(event))
                else:
                    async with self.container() as request:
                        handler = await request.get(type_handler.handler_type)
                        result.append(await handler.handle(event))

        return result

