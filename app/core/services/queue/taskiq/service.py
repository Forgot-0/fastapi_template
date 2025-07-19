from dataclasses import dataclass
from typing import Any, Optional
import asyncio

from app.core.services.queue.service import QueueServiceInterface, QueueResult, QueueResultStatus
from app.core.services.queue.task import BaseTask


@dataclass
class TaskiqQueueService(QueueServiceInterface):
    broker_url: str
    result_backend: str
    
    def __post_init__(self):
        """Initialize the queue service."""
        # For now, we'll implement a simple in-memory queue
        # In production, you'd integrate with actual Taskiq
        self._tasks = {}
        self._results = {}

    async def push(self, task: type[BaseTask], data: dict[str, Any]) -> QueueResult | None:
        """Push a task to the queue."""
        task_id = f"task_{len(self._tasks)}"
        
        # For demo purposes, execute immediately
        try:
            task_instance = task(**data)
            result = await task_instance.execute()
            
            queue_result = QueueResult(
                response={"task_id": task_id, "result": result},
                status=QueueResultStatus.SUCCESS
            )
            self._results[task_id] = queue_result
            return queue_result
            
        except Exception as e:
            queue_result = QueueResult(
                response={"task_id": task_id, "error": str(e)},
                status=QueueResultStatus.ERROR
            )
            self._results[task_id] = queue_result
            return queue_result

    async def is_ready(self, task_id: str) -> bool:
        """Check if task is ready."""
        return task_id in self._results

    async def get_result(self, task_id: str) -> QueueResult:
        """Get task result."""
        if task_id in self._results:
            return self._results[task_id]
        
        return QueueResult(
            response={"error": "Task not found"},
            status=QueueResultStatus.ERROR
        )

    async def wait_result(
        self, 
        task_id: str, 
        check_interval: Optional[float] = None, 
        timeout: Optional[float] = None
    ) -> QueueResult:
        """Wait for task result."""
        check_interval = check_interval or 1.0
        timeout = timeout or 30.0
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if await self.is_ready(task_id):
                return await self.get_result(task_id)
            
            if asyncio.get_event_loop().time() - start_time > timeout:
                return QueueResult(
                    response={"error": "Timeout waiting for task"},
                    status=QueueResultStatus.ERROR
                )
            
            await asyncio.sleep(check_interval)