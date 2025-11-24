from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.core.exceptions import FieldRequiredException


@dataclass
class BaseTask(ABC):
    @classmethod
    def get_name(cls) -> str:
        name = getattr(cls, "__task_name__", None)
        if name is None:
            raise FieldRequiredException

        return name

    @staticmethod
    @abstractmethod
    async def run(*args: Any, **kwargs: Any) -> None: ...
