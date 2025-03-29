from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Type

from app.core.command import CR, CT, BaseCommand, BaseCommandHandler
from app.core.query import QR, QT, BaseQuery, BaseQueryHandler




@dataclass(eq=False)
class Mediator:
    commands_map: dict[Type[BaseCommand], BaseCommandHandler] = field(
        default_factory=dict,
        kw_only=True
    )

    queries_map: dict[Type[BaseQuery], BaseQueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_command(self, command: Type[BaseCommand], command_handlers: BaseCommandHandler[CT, CR]):
        self.commands_map[command] = (command_handlers)

    def register_query(self, query: Type[BaseQuery], query_handler: BaseQueryHandler[QT, QR]):
        self.queries_map[query] = query_handler

    async def handle_command(self, command: BaseCommand) -> CR:
        return await self.commands_map[command.__class__].handle(command=command)

    async def handle_query(self, query: BaseQuery) -> QR:
        return await self.queries_map[query.__class__].handle(query=query)