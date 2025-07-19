from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Type

from app.core.events.event import ER, ET, BaseEvent, BaseEventHandler, EventHandlerRegistry


@dataclass(eq=False)
class BaseEventBus(ABC):
    event_registry: EventHandlerRegistry

    @abstractmethod
    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        ...


@dataclass(eq=False)
class EventBus(BaseEventBus):
    
    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        """Publish events to their registered handlers."""
        results = []
        
        handler_infos = self.event_registry.get_handler_types(events)
        
        for handler_info in handler_infos:
            for event in events:
                if handler_info.instance:
                    result = await handler_info.instance.handle(event)
                    results.append(result)
                # If no instance, we'd need to resolve from DI container
                # This would be handled by the DI integration
        
        return results