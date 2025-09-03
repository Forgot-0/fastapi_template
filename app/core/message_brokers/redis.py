from dataclasses import dataclass
from typing import Any, AsyncGenerator

import orjson
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from app.core.message_brokers.base import BaseMessageBroker
from app.core.message_brokers.converters import convert_dict_to_broker_message



@dataclass
class RedisMessageBroker(BaseMessageBroker):
    producer: Redis
    consumer: PubSub

    async def send_message(self, key: str, topic: str, value: bytes):
        data = {"key": key, "data": value.decode()}
        await self.producer.publish(
            channel=topic,
            message=convert_dict_to_broker_message(data)
        )

    async def send_data(self, key: str, topic: str, data: dict[str, Any]) -> None:
        data["key"] = key
        await self.producer.publish(
            channel=topic,
            message=convert_dict_to_broker_message(data)
        )

    async def start_consuming(self, topic: list[str]) -> AsyncGenerator[dict[str, Any], None]:
        await self.consumer.subscribe(*topic)

        async for message in self.consumer.listen():
            if message["type"] != "message":
                continue
            yield orjson.loads(message["data"])

    async def stop_consuming(self) -> None:
        self.consumer.unsubscribe()

    async def close(self) -> None:
        await self.consumer.close()
        await self.producer.close()

    async def start(self) -> None:
        return None