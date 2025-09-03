from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from dishka import Provider, Scope, provide

from app.core.configs.app import app_config
from app.core.message_brokers.base import BaseMessageBroker
from app.core.message_brokers.kafka import KafkaMessageBroker
# from app.core.message_brokers.redis import RedisMessageBroker




class BrokerProvider(Provider):
    scope = Scope.APP

    @provide
    def get_message_broker(self) -> BaseMessageBroker:
        return KafkaMessageBroker(
            consumer=AIOKafkaConsumer(
                bootstrap_servers=app_config.BROKER_URL,
                metadata_max_age_ms=30000,
                group_id=app_config.GROUP_ID
            ),
            producer=AIOKafkaProducer(bootstrap_servers=app_config.BROKER_URL)
        )