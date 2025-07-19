from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Type

from app.core.events.event import ER, ET, BaseEvent, BaseEventHandler, EventRegisty



@dataclass(eq=False)
class BaseEventBus(ABC):
    event_registy: EventRegisty

    @abstractmethod
    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        ...