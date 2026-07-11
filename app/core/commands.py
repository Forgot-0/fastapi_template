from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BaseCommand(ABC):
    ...


@dataclass(frozen=True)
class BaseCommandHandler[CT: BaseCommand, CR: Any](ABC):

    @abstractmethod
    async def handle(self, command: CT) -> CR: ...
