import asyncio
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

from app.core.websockets.base import BaseConnectionManager


@dataclass
class ConnectionManager(BaseConnectionManager):
    lock_map: dict[str, asyncio.Lock] = field(default_factory=dict)

    async def accept_connection(self, websocket: WebSocket, key: str, subprotocol: str | None=None) -> None:
        await websocket.accept(subprotocol=subprotocol)

        if key not in self.lock_map:
            self.lock_map[key] = asyncio.Lock()

        async with self.lock_map[key]:
            self.connections_map[key].append(websocket)

    async def remove_connection(self, websocket: WebSocket, key: str) -> None:
        async with self.lock_map[key]:
            self.connections_map[key].remove(websocket)
            if not self.connections_map[key]:
                del self.connections_map[key]
                del self.lock_map[key]

    async def send_all(self, key: str, bytes_: bytes) -> None:
        for websocket in self.connections_map[key]:
            try:
                await websocket.send_bytes(bytes_)
            except Exception:
                await self.remove_connection(websocket, key)

    async def send_json_all(self, key: str, data: dict[str, Any]) -> None:
        for websocket in self.connections_map[key]:
            try:
                await websocket.send_json(data)
            except Exception:
                await self.remove_connection(websocket, key)

    async def disconnect_all(self, key: str) -> None:
        async with self.lock_map[key]:
            for websocket in self.connections_map[key]:
                await websocket.send_json({
                    "message": "Abort connection",
                })
                await websocket.close()
