from dishka import AsyncContainer, Provider, Scope, provide

from app.core.events.event import EventRegisty
from app.core.events.mediator.service import MediatorEventBus
from app.core.events.service import BaseEventBus


class EventProvider(Provider):
    scope = Scope.APP

    @provide
    def event_handler_registry(self) -> EventRegisty:
        registry = EventRegisty()
        return registry

    @provide
    def event_bus(self, event_registy: EventRegisty, container: AsyncContainer) -> BaseEventBus:
        return MediatorEventBus(event_registy=event_registy, container=container)

