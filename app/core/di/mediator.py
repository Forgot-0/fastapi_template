from dishka import Provider, Scope, provide, Container

from app.core.mediators.imediator import DishkaMediator
from app.core.mediators.base import BaseMediator
from app.core.commands import CommandHandlerRegistry
from app.core.queries import QueryHandlerRegistry


class MediatorProvider(Provider):
    scope = Scope.APP

    @provide
    def command_registry(self) -> CommandHandlerRegistry:
        return CommandHandlerRegistry()

    @provide
    def query_registry(self) -> QueryHandlerRegistry:
        return QueryHandlerRegistry()

    @provide
    def mediator(
        self,
        container: Container,
        command_registry: CommandHandlerRegistry,
        query_registry: QueryHandlerRegistry,
    ) -> BaseMediator:
        mediator = DishkaMediator(container=container)
        mediator.command_registy = command_registry
        mediator.query_registy = query_registry
        return mediator