from dishka import AsyncContainer, Provider, Scope, provide
from dishka.integrations.taskiq import setup_dishka
from taskiq import AsyncBroker

from app.core.services.queue.taskiq.init import broker
from app.core.services.queue.service import QueueServiceInterface
from app.core.services.queue.taskiq.service import TaskiqQueueService


class QueueProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_broker(self, container: AsyncContainer) -> AsyncBroker:
        setup_dishka(container=container, broker=broker)
        return broker

    @provide
    async def get_queue_service(self, broker: AsyncBroker) -> QueueServiceInterface:
        return TaskiqQueueService(broker)