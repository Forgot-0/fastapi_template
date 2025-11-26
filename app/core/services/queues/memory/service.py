from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.core.services.queues.service import QueueResult, QueueResultStatus, QueueServiceInterface
from app.core.services.queues.task import BaseTask


@dataclass
class MemoryQueueServiceInterface(QueueServiceInterface):
    queue: dict[str, QueueResult] = field(default_factory=dict)

    async def push(self, task: type[BaseTask], data: dict[str, Any]) -> str:
        task_id = uuid4().hex
        self.queue[task_id] = QueueResult(response="Ok", status=QueueResultStatus.SUCCESS)
        return task_id

    async def is_ready(self, task_id: str) -> bool:
        return True

    async def get_result(self, task_id: str) -> QueueResult:
        return self.queue[task_id]

    async def wait_result(
        self, task_id: str, check_interval: float | None = None, timeout: float | None = None
    ) -> QueueResult:
        return self.queue[task_id]
