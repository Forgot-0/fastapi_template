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
    connections_map: dict[str, list[WebSocket]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    @abstractmethod
    async def accept_connection(self, websocket: WebSocket, key: str, subprotocol: str | None=None):
        ...

    @abstractmethod
    async def remove_connection(self, websocket: WebSocket, key: str):
        ...

    @abstractmethod
    async def send_all(self, key: str, bytes_: bytes):
        ...

    @abstractmethod
    async def send_json_all(self, key: str, data: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def disconnect_all(self, key: str):
        ...
