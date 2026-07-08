from dataclasses import dataclass
from typing import Any

from dishka import AsyncContainer

from app.core.commands import BaseCommand
from app.core.exceptions import NotHandlerRegisterError
from app.core.mediators.base import BaseMediator
from app.core.queries import BaseQuery


@dataclass(eq=False)
class DishkaMediator(BaseMediator):
    container: AsyncContainer

    async def handle_command(self, command: BaseCommand) -> Any:
        handler_type = self.command_registy.get_handler_types(command)
        if not handler_type:
            raise NotHandlerRegisterError(classes=[command.__class__.__name__])

        async with self.container() as requests_container:
            handler = await requests_container.get(handler_type)
            return await handler.handle(command)

    async def handle_query(self, query: BaseQuery) -> Any:
        handler_type = self.query_registy.get_handler_types(query)
        if handler_type is None:
            raise NotHandlerRegisterError(classes=[query.__class__.__name__])

        async with self.container() as requests_container:
            handler = await requests_container.get(handler_type)
            return await handler.handle(query)
