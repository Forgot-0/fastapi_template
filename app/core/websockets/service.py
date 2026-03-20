import asyncio
from dataclasses import dataclass, field
import logging
from typing import Any

from fastapi import WebSocket
import orjson
from redis.asyncio import Redis

from app.core.websockets.base import BaseConnectionManager


logger = logging.getLogger(__name__)


@dataclass
class ConnectionManager(BaseConnectionManager):
    redis: Redis
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
            except Exception as ex:
                await self.remove_connection(websocket, key)

    async def disconnect_all(self, key: str) -> None:
        async with self.lock_map[key]:
            for websocket in self.connections_map[key]:
                await websocket.send_json({
                    "message": "Abort connection",
                })
                await websocket.close()

    async def publish(self, connection_id: str, payload: dict) -> None:
        await self.redis.publish(
            f"ws:{connection_id}",
            orjson.dumps(payload),
        )

    async def startup(self) -> None:
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe("ws:*")

        try:
            async for message in pubsub.listen():
                if message["type"] != "pmessage":
                    continue
                channel: bytes = message["channel"]
                connection_id = channel.decode().removeprefix("ws:")
                try:
                    payload = orjson.loads(message["data"])
                except Exception as ex:
                    logger.error("Bad JSON in channel %s", channel)
                    continue

                delivered = await self.send_json_all(connection_id, payload)
                if not delivered:
                    logger.debug(
                        "connection_id %s not on this instance, skipped",
                        connection_id,
                    )
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.exception("Pub/Sub listener crashed: %s", exc)
        finally:
            await pubsub.unsubscribe()
            await self.redis.aclose()

    async def shutdown(self) -> None:
        if self.redis:
            await self.redis.aclose()

        logger.info("ConnectionManager stopped")
