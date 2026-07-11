from dishka import AsyncContainer, Provider, Scope, provide

from app.core.mediators.base import BaseMediator, CommandRegistry, QueryRegistry
from app.core.mediators.imediator import DishkaMediator


class MediatorProvider(Provider):
    scope = Scope.APP

    @provide
    def command_registry(self) -> CommandRegistry:
        registry = CommandRegistry()
        return registry

    @provide
    def query_registry(self) -> QueryRegistry:
        registry = QueryRegistry()
        return registry

    @provide
    def mediator(
        self,
        container: AsyncContainer,
        command_registry: CommandRegistry,
        query_registry: QueryRegistry,
    ) -> BaseMediator:
        mediator = DishkaMediator(
            container=container,
            query_registry=query_registry,
            command_registry=command_registry
        )

        return mediator
