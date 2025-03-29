from abc import ABC, abstractmethod


class BaseTask(ABC):
    @classmethod
    def get_name(cls) -> str:
        name = getattr(cls, '__task_name__', None)
        if name is None:
            raise 

        return name

    @abstractmethod
    def run(self, *args, **kwargs):
        ...