from dishka import Provider, Scope, provide
from taskiq import AsyncBroker, InMemoryBroker
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.core.configs.app import app_config
from app.core.services.queue.service import QueueServiceInterface
from app.core.services.queue.taskiq.service import TaskiqQueueService


class QueueProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_broker(self) -> AsyncBroker:
        if app_config.ENVIRONMENT == 'testing':
            broker = InMemoryBroker()
        else:
            broker = ListQueueBroker(url=app_config.QUEUE_REDIS_BROKER_URL)
            broker.with_result_backend(RedisAsyncResultBackend(app_config.QUEUE_REDIS_RESULT_BACKEND))
        return broker

    @provide
    async def get_queue_service(self, broker: AsyncBroker) -> QueueServiceInterface:
        return TaskiqQueueService(broker)