from dishka import Provider, Scope, provide
from taskiq import AsyncBroker

from app.core.services.queue.taskiq.init import broker
from app.core.services.queue.service import QueueServiceInterface
from app.core.services.queue.taskiq.service import TaskiqQueueService


class QueueProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_broker(self) -> AsyncBroker:
        return broker

    @provide
    async def get_queue_service(self, broker: AsyncBroker) -> QueueServiceInterface:
        return TaskiqQueueService(broker)