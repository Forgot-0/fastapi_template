from typing import Any

from app.core.services.queue.service import QueueServiceInterface
from app.core.services.queue.taskiq.decorator import TaskiqQueuedDecorator
from app.core.services.queue.taskiq.service import TaskiqQueueService
from app.core.services.queue.taskiq.init import broker


def get_queue_service() -> QueueServiceInterface:
    return TaskiqQueueService(broker)


def get_queued_decorator() -> Any:
    return TaskiqQueuedDecorator(broker)