import asyncio
from abc import (
    ABC,
    abstractmethod,
)
from collections import defaultdict
from dataclasses import (
    dataclass,
    field,
)
from typing import Any

from fastapi import WebSocket


@dataclass
class BaseConnectionManager(ABC):
    connections_map: dict[str, set[WebSocket]] = field(
        default_factory=lambda: defaultdict(set),
        kw_only=True,
    )
    heartbeat_interval: int = field(default=30, kw_only=True)
    heartbeat_task: asyncio.Task | None = field(default=None, kw_only=True)

    @abstractmethod
    async def accept_connection(self, websocket: WebSocket, key: str, subprotocol: str | None=None) -> None:
        ...

    @abstractmethod
    async def bind_connection(self, websocket: WebSocket, key: str) -> None:
        ...

    @abstractmethod
    async def bind_key_connections(self, source_key: str, target_key: str) -> None:
        ...

    @abstractmethod
    async def unbind_key_connections(self, source_key: str, target_key: str) -> None:
        ...

    @abstractmethod
    async def remove_connection(self, websocket: WebSocket, key: str) -> None:
        ...

    @abstractmethod
    async def send_all(self, key: str, bytes_: bytes) -> None:
        ...

    @abstractmethod
    async def send_json_all(self, key: str, data: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def disconnect_all(self, key: str) -> None:
        ...

    @abstractmethod
    async def publish(self, key: str, payload: dict) -> None:
        ...

    @abstractmethod
    async def publish_bulk(self, keys: list[str], payload: dict) -> None:
        ...

    @abstractmethod
    async def startup(self) -> None:
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        ...
