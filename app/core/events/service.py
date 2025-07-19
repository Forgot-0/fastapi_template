from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Type, Optional, Any

from app.core.events.event import ER, ET, BaseEvent, BaseEventHandler, EventHandlerRegistry


@dataclass(eq=False)
class BaseEventBus(ABC):
    event_registry: EventHandlerRegistry

    @abstractmethod
    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        ...


@dataclass(eq=False)
class EventBus(BaseEventBus):
    """Simple EventBus that works with pre-instantiated handlers."""
    
    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        """Publish events to their registered handlers."""
        results = []
        
        handler_infos = self.event_registry.get_handler_types(events)
        
        for handler_info in handler_infos:
            for event in events:
                if handler_info.instance:
                    result = await handler_info.instance.handle(event)
                    results.append(result)
                else:
                    # No instance available - skip this handler
                    # This is where DI integration would be needed
                    pass
        
        return results


@dataclass(eq=False)
class DIEventBus(BaseEventBus):
    """DI-aware EventBus that resolves handlers from the container."""
    
    def __init__(self, event_registry: EventHandlerRegistry, container: Optional[Any] = None):
        self.event_registry = event_registry
        self.container = container
    
    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        """Publish events to handlers resolved from DI container."""
        if not self.container:
            # Fall back to simple behavior if no container
            return await super().publish(events)
        
        results = []
        
        handler_infos = self.event_registry.get_handler_types(events)
        
        for handler_info in handler_infos:
            for event in events:
                try:
                    # Try to resolve handler from DI container
                    if handler_info.instance:
                        # Use pre-instantiated handler
                        handler = handler_info.instance
                    else:
                        # Resolve handler from DI container with dependencies
                        with self.container() as request_scope:
                            handler = request_scope.get(handler_info.handler_type)
                    
                    result = await handler.handle(event)
                    results.append(result)
                    
                except Exception as e:
                    # Log error but continue processing other handlers
                    print(f"Error handling event {type(event).__name__} with handler {handler_info.handler_type.__name__}: {e}")
                    continue
        
        return results


class EventBusContextManager:
    """Context manager for EventBus that provides request-scoped container access."""
    
    def __init__(self, event_bus: DIEventBus, container: Any):
        self.event_bus = event_bus
        self.container = container
        self._original_container = None
    
    def __enter__(self) -> DIEventBus:
        self._original_container = self.event_bus.container
        self.event_bus.container = self.container
        return self.event_bus
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.event_bus.container = self._original_container


@dataclass(eq=False) 
class RequestScopedEventBus(BaseEventBus):
    """EventBus that creates a new request scope for each publish operation."""
    
    def __init__(self, event_registry: EventHandlerRegistry, container: Any):
        self.event_registry = event_registry
        self.container = container
    
    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        """Publish events with fresh request scope for each operation."""
        results = []
        
        handler_infos = self.event_registry.get_handler_types(events)
        
        # Create a single request scope for this publish operation
        with self.container() as request_scope:
            for handler_info in handler_infos:
                for event in events:
                    try:
                        if handler_info.instance:
                            # Use pre-instantiated handler
                            handler = handler_info.instance
                        else:
                            # Resolve handler with all its dependencies
                            handler = request_scope.get(handler_info.handler_type)
                        
                        result = await handler.handle(event)
                        results.append(result)
                        
                    except Exception as e:
                        # Log error but continue processing
                        print(f"Error handling event {type(event).__name__} with handler {handler_info.handler_type.__name__}: {e}")
                        continue
        
        return results