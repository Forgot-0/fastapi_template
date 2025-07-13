from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Type

from app.core.events.event import ER, ET, BaseEvent, BaseEventHandler



@dataclass(eq=False)
class BaseEventBus(ABC):

    @abstractmethod
    def __call__(self, event: Type[BaseEvent]) -> None:
        ...

    @abstractmethod
    def subscribe(self, event: Type[BaseEvent], event_handlers: Iterable[BaseEventHandler[ET, ER]]):
        ...

    @abstractmethod
    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        ...