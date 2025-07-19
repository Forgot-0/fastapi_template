from dishka import Provider, Scope, provide, Container

from app.core.events.service import BaseEventBus, EventBus, DIEventBus, RequestScopedEventBus
from app.core.events.event import EventHandlerRegistry


class EventProvider(Provider):
    scope = Scope.APP

    @provide
    def event_handler_registry(self) -> EventHandlerRegistry:
        """Provide the event handler registry."""
        return EventHandlerRegistry()

    @provide
    def simple_event_bus(self, event_registry: EventHandlerRegistry) -> EventBus:
        """Provide simple EventBus for pre-instantiated handlers."""
        return EventBus(event_registry=event_registry)

    @provide
    def di_event_bus(self, event_registry: EventHandlerRegistry, container: Container) -> DIEventBus:
        """Provide DI-aware EventBus that resolves handlers from container."""
        return DIEventBus(event_registry=event_registry, container=container)

    @provide
    def request_scoped_event_bus(self, event_registry: EventHandlerRegistry, container: Container) -> RequestScopedEventBus:
        """Provide request-scoped EventBus (recommended for most use cases)."""
        return RequestScopedEventBus(event_registry=event_registry, container=container)

    @provide
    def event_bus(self, request_scoped_event_bus: RequestScopedEventBus) -> BaseEventBus:
        """Provide the default EventBus implementation (request-scoped)."""
        return request_scoped_event_bus


class RequestEventProvider(Provider):
    """Alternative provider that creates request-scoped event bus instances."""
    scope = Scope.REQUEST

    @provide
    def request_event_bus(
        self, 
        event_registry: EventHandlerRegistry, 
        container: Container
    ) -> RequestScopedEventBus:
        """Provide a fresh request-scoped EventBus for each request."""
        return RequestScopedEventBus(event_registry=event_registry, container=container)