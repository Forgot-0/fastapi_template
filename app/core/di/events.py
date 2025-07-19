from dishka import Provider, provide, Scope, Container

from app.core.events.service import BaseEventBus
from app.core.events.mediator.service import MediatorEventBus
from app.core.events.event import EventRegisty


class EventsProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_event_registry(self) -> EventRegisty:
        registry = EventRegisty()
        # Add event handlers here when they exist
        return registry

    @provide
    def get_event_bus(self, container: Container, event_registry: EventRegisty) -> BaseEventBus:
        return MediatorEventBus(container=container, event_registy=event_registry)