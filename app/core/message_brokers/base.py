from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from app.core.events.event import BaseEvent


@dataclass
class BaseMessageBroker(ABC):

    @abstractmethod
    async def start(self) -> None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    @abstractmethod
    async def send_message(self, key: bytes, topic: str, value: bytes) -> None:
        ...

    @abstractmethod
    async def send_data(self, key: str, topic: str, data: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def send_event(self, key: str, event: BaseEvent) -> None:
        ...

    @abstractmethod
    async def start_consuming(self, topic: list[str]) -> AsyncGenerator[dict[str, Any], None]:
        ...

    @abstractmethod
    async def stop_consuming(self) -> None:
        ...
