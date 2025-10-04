from dataclasses import dataclass
import functools
from taskiq import AsyncBroker

from app.core.services.queue.task import BaseTask


@dataclass
class TaskiqQueuedDecorator:
    broker: AsyncBroker

    def __call__(self, cls: type[BaseTask]) -> type[BaseTask]:

        self.broker.register_task(func=cls.run, task_name=cls.get_name())

        async def wrapper(*args, **kwargs):
            return await cls.run(*args, **kwargs)

        functools.update_wrapper(wrapper, cls.run, assigned=("__doc__",), updated=())

        self.broker.register_task(func=wrapper, task_name=cls.get_name())

        return cls