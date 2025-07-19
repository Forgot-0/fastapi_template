"""
Enhanced event registration system for DI integration.

This module provides utilities for registering event handlers with the DI system,
supporting both pre-instantiated handlers and DI-resolved handlers.
"""

from typing import Type, List, Optional, Any
from dataclasses import dataclass

from app.core.events.event import BaseEvent, BaseEventHandler, EventHandlerRegistry, EventHandlerInfo


@dataclass
class EventHandlerConfig:
    """Configuration for event handler registration."""
    event_type: Type[BaseEvent]
    handler_type: Type[BaseEventHandler]
    instance: Optional[BaseEventHandler] = None
    use_di: bool = True


class DIEventRegistration:
    """Enhanced event registration that supports DI."""
    
    def __init__(self, registry: EventHandlerRegistry, container: Optional[Any] = None):
        self.registry = registry
        self.container = container
        self._handler_configs: List[EventHandlerConfig] = []
    
    def register_handler(
        self, 
        event_type: Type[BaseEvent], 
        handler_type: Type[BaseEventHandler],
        instance: Optional[BaseEventHandler] = None,
        use_di: bool = True
    ) -> None:
        """Register an event handler with optional DI integration."""
        config = EventHandlerConfig(
            event_type=event_type,
            handler_type=handler_type,
            instance=instance,
            use_di=use_di
        )
        
        self._handler_configs.append(config)
        
        # Register with the registry
        handler_info = EventHandlerInfo(
            handler_type=handler_type,
            instance=instance if not use_di else None
        )
        
        self.registry.subscribe(event_type, [handler_info])
    
    def register_multiple_handlers(
        self, 
        event_type: Type[BaseEvent], 
        handler_types: List[Type[BaseEventHandler]],
        use_di: bool = True
    ) -> None:
        """Register multiple handlers for the same event."""
        for handler_type in handler_types:
            self.register_handler(event_type, handler_type, use_di=use_di)
    
    def register_handler_for_multiple_events(
        self,
        event_types: List[Type[BaseEvent]],
        handler_type: Type[BaseEventHandler],
        use_di: bool = True
    ) -> None:
        """Register the same handler for multiple events."""
        for event_type in event_types:
            self.register_handler(event_type, handler_type, use_di=use_di)
    
    def get_handler_configs(self) -> List[EventHandlerConfig]:
        """Get all registered handler configurations."""
        return self._handler_configs.copy()
    
    def get_di_handlers(self) -> List[EventHandlerConfig]:
        """Get handlers that use DI."""
        return [config for config in self._handler_configs if config.use_di]
    
    def get_instance_handlers(self) -> List[EventHandlerConfig]:
        """Get handlers that use pre-instantiated instances."""
        return [config for config in self._handler_configs if not config.use_di and config.instance]


class EventHandlerFactory:
    """Factory for creating event handlers with DI support."""
    
    def __init__(self, container: Any):
        self.container = container
    
    def create_handler(self, handler_type: Type[BaseEventHandler]) -> BaseEventHandler:
        """Create a handler instance with DI."""
        with self.container() as request_scope:
            return request_scope.get(handler_type)
    
    def create_handlers(self, handler_types: List[Type[BaseEventHandler]]) -> List[BaseEventHandler]:
        """Create multiple handler instances with DI."""
        handlers = []
        with self.container() as request_scope:
            for handler_type in handler_types:
                handler = request_scope.get(handler_type)
                handlers.append(handler)
        return handlers


def register_event_handlers_with_di(
    registry: EventHandlerRegistry,
    container: Any,
    handler_configs: List[EventHandlerConfig]
) -> DIEventRegistration:
    """Register multiple event handlers with DI support."""
    registration = DIEventRegistration(registry, container)
    
    for config in handler_configs:
        registration.register_handler(
            event_type=config.event_type,
            handler_type=config.handler_type,
            instance=config.instance,
            use_di=config.use_di
        )
    
    return registration


# Convenience functions for common registration patterns

def register_auth_events_with_di(registration: DIEventRegistration) -> None:
    """Register auth module events with DI."""
    from app.auth.events.users.created import CreatedUserEvent, CreatedUserEventHandler
    from app.auth.events.users.verified import VerifiedUserEvent, VerifiedUserEventHandler
    from app.auth.events.users.password_reset import PasswordResetEvent, PasswordResetEventHandler
    
    # Register with DI (handlers will get dependencies injected)
    registration.register_handler(CreatedUserEvent, CreatedUserEventHandler, use_di=True)
    registration.register_handler(VerifiedUserEvent, VerifiedUserEventHandler, use_di=True)
    registration.register_handler(PasswordResetEvent, PasswordResetEventHandler, use_di=True)


def register_core_events_with_di(registration: DIEventRegistration) -> None:
    """Register core module events with DI."""
    # Add core event registrations here as they're created
    pass


def create_full_event_registration(
    registry: EventHandlerRegistry, 
    container: Any
) -> DIEventRegistration:
    """Create a complete event registration with all handlers."""
    registration = DIEventRegistration(registry, container)
    
    # Register all modules
    register_auth_events_with_di(registration)
    register_core_events_with_di(registration)
    
    return registration