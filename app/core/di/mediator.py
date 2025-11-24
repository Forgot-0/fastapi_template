from dishka import AsyncContainer, Provider, Scope, provide

from app.core.mediators.base import BaseMediator
from app.core.mediators.command import CommandRegisty
from app.core.mediators.imediator import DishkaMediator
from app.core.mediators.query import QueryRegistry


class MediatorProvider(Provider):
    scope = Scope.APP

    @provide
    def command_registry(self) -> CommandRegisty:
        registry = CommandRegisty()
        return registry

    @provide
    def query_registry(self) -> QueryRegistry:
        registry = QueryRegistry()
        return registry

    @provide
    def mediator(
        self,
        container: AsyncContainer,
        command_registry: CommandRegisty,
        query_registry: QueryRegistry,
    ) -> BaseMediator:
        mediator = DishkaMediator(
            container=container,
            query_registy=query_registry,
            command_registy=command_registry
        )

        return mediator
