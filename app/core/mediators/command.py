from abc import (
    ABC,
    abstractmethod,
)
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import (
    dataclass,
    field,
)
from typing import Optional, Type

from app.core.commands import CR, BaseCommand, BaseCommandHandler


@dataclass
class HandlerInfo:
    handler_type: Type[BaseCommandHandler]
    instance: Optional[BaseCommandHandler] = None



@dataclass
class CommandRegisty:
    commands_map: dict[Type[BaseCommand], list[HandlerInfo]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    def register_command(self, command: Type[BaseCommand], type_handlers: Iterable[HandlerInfo]) -> None:
        self.commands_map[command].extend(type_handlers)

    def get_handler_types(self, command: BaseCommand) -> Iterable[HandlerInfo]:
        return self.commands_map.get(command.__class__, [])



@dataclass(eq=False)
class CommandMediator(ABC):
    command_registy: CommandRegisty

    @abstractmethod
    async def handle_command(self, command: BaseCommand) -> Iterable[CR]:
        ...