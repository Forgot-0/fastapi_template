from dishka import Provider, Scope, provide

from app.core.events.service import BaseEventBus, EventBus
from app.core.events.event import EventHandlerRegistry


class EventProvider(Provider):
    scope = Scope.APP

    @provide
    def event_handler_registry(self) -> EventHandlerRegistry:
        return EventHandlerRegistry()

    @provide
    def event_bus(self, event_registry: EventHandlerRegistry) -> BaseEventBus:
        return EventBus(event_registry=event_registry)