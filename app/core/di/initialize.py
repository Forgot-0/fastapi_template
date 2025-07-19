"""
DI System Initialization

This module provides functions to initialize the complete DI system,
including registering all command handlers, query handlers, and event handlers.
"""

from typing import Any

from app.core.di.container import get_container
from app.core.commands import CommandHandlerRegistry
from app.core.queries import QueryHandlerRegistry
from app.core.events.event import EventHandlerRegistry, EventHandlerInfo

# Import all command types and handlers
from app.auth.commands.users.register import RegisterCommand, RegisterCommandHandler
from app.auth.commands.users.verify import VerifyCommand, VerifyCommandHandler
from app.auth.commands.users.send_verify import SendVerifyCommand, SendVerifyCommandHandler
from app.auth.commands.users.reset_password import ResetPasswordCommand, ResetPasswordCommandHandler
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand, SendResetPasswordCommandHandler
from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.commands.auth.logout import LogoutCommand, LogoutCommandHandler
from app.auth.commands.auth.refresh_token import RefreshTokenCommand, RefreshTokenCommandHandler

# Import all query types and handlers
from app.auth.queries.users.get_by_id import GetUserByIdQuery, GetUserByIdQueryHandler
from app.auth.queries.users.get_by_email import GetUserByEmailQuery, GetUserByEmailQueryHandler
from app.auth.queries.users.get_list import GetUserListQuery, GetUserListQueryHandler
from app.auth.queries.auth.get_current_user import GetCurrentUserQuery, GetCurrentUserQueryHandler

# Import all event types and handlers
from app.auth.events.users.created import CreatedUserEvent, CreatedUserEventHandler
from app.auth.events.users.verified import VerifiedUserEvent, VerifiedUserEventHandler
from app.auth.events.users.password_reset import PasswordResetEvent, PasswordResetEventHandler


def register_command_handlers(command_registry: CommandHandlerRegistry) -> None:
    """Register all command handlers with the command registry."""
    
    # User commands
    command_registry.register(RegisterCommand, RegisterCommandHandler)
    command_registry.register(VerifyCommand, VerifyCommandHandler)
    command_registry.register(SendVerifyCommand, SendVerifyCommandHandler)
    command_registry.register(ResetPasswordCommand, ResetPasswordCommandHandler)
    command_registry.register(SendResetPasswordCommand, SendResetPasswordCommandHandler)
    
    # Auth commands
    command_registry.register(LoginCommand, LoginCommandHandler)
    command_registry.register(LogoutCommand, LogoutCommandHandler)
    command_registry.register(RefreshTokenCommand, RefreshTokenCommandHandler)


def register_query_handlers(query_registry: QueryHandlerRegistry) -> None:
    """Register all query handlers with the query registry."""
    
    # User queries
    query_registry.register(GetUserByIdQuery, GetUserByIdQueryHandler)
    query_registry.register(GetUserByEmailQuery, GetUserByEmailQueryHandler)
    query_registry.register(GetUserListQuery, GetUserListQueryHandler)
    
    # Auth queries
    query_registry.register(GetCurrentUserQuery, GetCurrentUserQueryHandler)


def register_event_handlers(event_registry: EventHandlerRegistry) -> None:
    """Register all event handlers with the event registry."""
    
    # User events
    event_registry.subscribe(CreatedUserEvent, [
        EventHandlerInfo(handler_type=CreatedUserEventHandler)
    ])
    
    event_registry.subscribe(VerifiedUserEvent, [
        EventHandlerInfo(handler_type=VerifiedUserEventHandler)
    ])
    
    event_registry.subscribe(PasswordResetEvent, [
        EventHandlerInfo(handler_type=PasswordResetEventHandler)
    ])


def initialize_di_system() -> None:
    """
    Initialize the complete DI system.
    
    This function should be called during application startup to register
    all handlers with their respective registries.
    """
    container = get_container()
    
    try:
        with container() as app_scope:
            # Get registries from DI container
            command_registry = app_scope.get(CommandHandlerRegistry)
            query_registry = app_scope.get(QueryHandlerRegistry)  
            event_registry = app_scope.get(EventHandlerRegistry)
            
            # Register all handlers
            register_command_handlers(command_registry)
            register_query_handlers(query_registry)
            register_event_handlers(event_registry)
            
            print("✅ DI System initialized successfully")
            print(f"   - Registered {len(command_registry._handlers)} command types")
            print(f"   - Registered {len(query_registry._handlers)} query types")
            print(f"   - Registered {len(event_registry.events_map)} event types")
            
    except Exception as e:
        print(f"❌ Failed to initialize DI system: {e}")
        raise


def get_registered_handlers_info() -> dict[str, Any]:
    """Get information about registered handlers for debugging."""
    container = get_container()
    
    with container() as app_scope:
        command_registry = app_scope.get(CommandHandlerRegistry)
        query_registry = app_scope.get(QueryHandlerRegistry)
        event_registry = app_scope.get(EventHandlerRegistry)
        
        return {
            "commands": {
                cmd_type.__name__: [h.handler_type.__name__ for h in handlers]
                for cmd_type, handlers in command_registry._handlers.items()
            },
            "queries": {
                query_type.__name__: handler_info.handler_type.__name__
                for query_type, handler_info in query_registry._handlers.items()
            },
            "events": {
                event_type.__name__: [h.handler_type.__name__ for h in handlers]
                for event_type, handlers in event_registry.events_map.items()
            }
        }


# Convenience function for FastAPI startup
async def startup_di_system():
    """Async startup function for FastAPI lifespan events."""
    initialize_di_system()


# Convenience function for FastAPI shutdown  
async def shutdown_di_system():
    """Async shutdown function for FastAPI lifespan events."""
    print("🔄 Shutting down DI system...")
    # Add any cleanup logic here if needed