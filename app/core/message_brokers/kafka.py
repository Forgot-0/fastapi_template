from dataclasses import dataclass
from typing import Any, AsyncIterator

import orjson
from aiokafka import AIOKafkaConsumer
from aiokafka.producer import AIOKafkaProducer

from app.core.events.event import BaseEvent
from app.core.message_brokers.base import BaseMessageBroker
from app.core.message_brokers.converters import (
    convert_dict_to_broker_message,
    convert_event_to_broker_message
)



@dataclass
class KafkaMessageBroker(BaseMessageBroker):
    producer: AIOKafkaProducer
    consumer: AIOKafkaConsumer

    async def send_message(self, key: bytes, topic: str, value: bytes) -> None:
        await self.producer.send(topic=topic, key=key, value=value)

    async def send_data(self, key: str, topic: str, data: dict[str, Any]) -> None:
        data['key'] = key
        value = convert_dict_to_broker_message(data)
        await self.producer.send(topic=topic, key=key.encode(), value=value)

    async def send_event(self, key: str, event: BaseEvent) -> None:
        value = convert_event_to_broker_message(event)
        await self.producer.send(
            topic=event.get_name(),
            key=key.encode(),
            value=value,
        )

    async def start_consuming(self, topic: list[str]) -> AsyncIterator[dict]:
        self.consumer.subscribe(topics=topic)

        async for message in self.consumer:
            yield orjson.loads(message.value) # type: ignore

    async def stop_consuming(self) -> None:
        self.consumer.unsubscribe()

    async def close(self) -> None:
        await self.consumer.stop()
        await self.producer.stop()

    async def start(self) -> None:
        await self.producer.start()
        await self.consumer.start()