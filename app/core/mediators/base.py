
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable

from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass
class CommandRegisty:
    commands_map: dict[type[BaseCommand], list[type[BaseCommandHandler]]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    def register_command(self, command: type[BaseCommand], type_handlers: Iterable[type[BaseCommandHandler]]) -> None:
        self.commands_map[command].extend(type_handlers)

    def get_handler_types(self, command: BaseCommand) -> Iterable[type[BaseCommandHandler]]:
        return self.commands_map.get(command.__class__, [])



@dataclass
class QueryRegistry:
    queries_map: dict[type[BaseQuery], type[BaseQueryHandler]] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_query(self, query: type[BaseQuery], type_handler: type[BaseQueryHandler]) -> None:
        self.queries_map[query] = type_handler

    def get_handler_types(self, query: BaseQuery) -> type[BaseQueryHandler]  | None:
        return self.queries_map.get(query.__class__)



@dataclass(eq=False)
class BaseMediator(ABC):
    command_registy: CommandRegisty
    query_registy: QueryRegistry

    @abstractmethod
    async def handle_query(self, query: BaseQuery) -> Any:
        ...

    @abstractmethod
    async def handle_command(self, command: BaseCommand) -> Iterable[Any]:
        ...

