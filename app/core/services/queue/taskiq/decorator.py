from dataclasses import dataclass
from taskiq import AsyncBroker

from app.core.services.queue.task import BaseTask


@dataclass
class TaskiqQueuedDecorator:
    broker: AsyncBroker

    def __call__(self, cls: type[BaseTask]) -> type[BaseTask]:

        async def task_wrapper(*args, **kwargs):
            task_instance = cls()
            return await task_instance.run(*args, **kwargs) # type: ignore

        task_wrapper.name = cls.get_name()

        self.broker.register_task(func=task_wrapper, task_name=cls.get_name())

        return cls