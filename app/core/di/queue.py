from dishka import AsyncContainer, Provider, Scope, provide
from dishka.integrations.taskiq import setup_dishka
from taskiq import AsyncBroker, InMemoryBroker
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.core.configs.app import app_config
from app.core.di.tasks import regester_core_task
from app.core.services.mail.aiosmtplib.task import SendEmail
from app.core.services.queue.service import QueueServiceInterface
from app.core.services.queue.taskiq.service import TaskiqQueueService


class QueueProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_broker(self, container: AsyncContainer) -> AsyncBroker:
        broker: AsyncBroker

        if app_config.ENVIRONMENT == 'testing':
            broker = InMemoryBroker()
        else:
            broker = ListQueueBroker(url=app_config.QUEUE_REDIS_BROKER_URL)
            broker.with_result_backend(RedisAsyncResultBackend(app_config.QUEUE_REDIS_RESULT_BACKEND))

        setup_dishka(container=container, broker=broker)

        regester_core_task(broker)
        return broker

    @provide
    async def get_queue_service(self, broker: AsyncBroker) -> QueueServiceInterface:
        return TaskiqQueueService(broker)