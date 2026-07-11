from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass
class CommandRegistry:
    commands_map: dict[type[BaseCommand], type[BaseCommandHandler]] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_command(self, command: type[BaseCommand], type_handler: type[BaseCommandHandler]) -> None:
        self.commands_map[command] = type_handler

    def get_handler_types(self, command: BaseCommand) -> type[BaseCommandHandler] | None:
        return self.commands_map.get(command.__class__)


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
    command_registry: CommandRegistry
    query_registry: QueryRegistry

    @abstractmethod
    async def handle_query(self, query: BaseQuery) -> Any:
        ...

    @abstractmethod
    async def handle_command(self, command: BaseCommand) -> Any:
        ...

