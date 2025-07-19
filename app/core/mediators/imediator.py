
from collections.abc import Iterable
from dataclasses import dataclass

from dishka import AsyncContainer


from app.core.commands import CR, BaseCommand
from app.core.mediators.base import BaseMediator
from app.core.queries import QR, BaseQuery


@dataclass(eq=False)
class DishkaMediator(BaseMediator):
    container: AsyncContainer

    async def handle_command(self, command: BaseCommand) -> Iterable[CR]:
        result = []

        handler_registy = self.command_registy.get_handler_types(command)
        if not handler_registy:
            raise 

        for handler in handler_registy:
            if handler.instance:
                result.append(await handler.instance.handle(command))
            else:
                async with self.container() as request:
                    handler = await request.get(handler.handler_type)
                    result.append(await handler.handle(command))

        return result

    async def handle_query(self, query: BaseQuery) -> QR:
        handler_registy = self.query_registy.get_handler_types(query)
        if handler_registy.instance:
            return await handler_registy.instance.handle(query)

        async with self.container() as request:
            handler = await request.get(handler_registy.handler_type)
            return await handler.handle(query)