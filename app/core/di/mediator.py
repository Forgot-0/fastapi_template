from dishka import AsyncContainer, Provider, Scope, provide

from app.auth.di.handlers import register_auth_command_handlers, register_auth_query_handlers
from app.core.mediators.command import CommandRegisty
from app.core.mediators.imediator import DishkaMediator
from app.core.mediators.base import BaseMediator
from app.core.mediators.query import QueryRegisty



class MediatorProvider(Provider):
    scope = Scope.APP

    @provide
    def command_registry(self) -> CommandRegisty:
        registry = CommandRegisty()
        register_auth_command_handlers(registry)
        return registry

    @provide
    def query_registry(self) -> QueryRegisty:
        registry = QueryRegisty()
        register_auth_query_handlers(registry)
        return registry

    @provide
    def mediator(
        self,
        container: AsyncContainer,
        command_registry: CommandRegisty,
        query_registry: QueryRegisty,
    ) -> BaseMediator:
        mediator = DishkaMediator(
            container=container,
            query_registy=query_registry,
            command_registy=command_registry
        )

        return mediator