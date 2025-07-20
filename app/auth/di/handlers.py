from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.commands.auth.logout import LogoutCommand, LogoutCommandHandler
from app.auth.commands.auth.refresh_token import RefreshTokenCommand, RefreshTokenCommandHandler
from app.auth.commands.users.register import RegisterCommand, RegisterCommandHandler
from app.auth.commands.users.reset_password import ResetPasswordCommand, ResetPasswordCommandHandler
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand, SendResetPasswordCommandHandler
from app.auth.commands.users.send_verify import SendVerifyCommand, SendVerifyCommandHandler
from app.auth.commands.users.verify import VerifyCommand, VerifyCommandHandler
from app.auth.events.users.created import CreatedUserEvent, SendVerifyEventHandler
from app.auth.queries.auth.get_by_token import GetByAcccessTokenQuery, GetByAcccessTokenQueryHandler
from app.core.events.event import EventHandlerInfo, EventRegisty
from app.core.mediators.command import HandlerInfo, CommandRegisty
from app.core.mediators.query import QueryHandlerInfo, QueryRegisty


def register_auth_command_handlers(command_registry: CommandRegisty) -> None:
    """Register all command handlers with the command registry."""

    # User commands
    command_registry.register_command(RegisterCommand, [HandlerInfo(RegisterCommandHandler)])
    command_registry.register_command(VerifyCommand, [HandlerInfo(VerifyCommandHandler)])
    command_registry.register_command(SendVerifyCommand, [HandlerInfo(SendVerifyCommandHandler)])
    command_registry.register_command(ResetPasswordCommand, [HandlerInfo(ResetPasswordCommandHandler)])
    command_registry.register_command(SendResetPasswordCommand, [HandlerInfo(SendResetPasswordCommandHandler)])

    # Auth commands
    command_registry.register_command(LoginCommand, [HandlerInfo(LoginCommandHandler)])
    command_registry.register_command(LogoutCommand, [HandlerInfo(LogoutCommandHandler)])
    command_registry.register_command(RefreshTokenCommand, [HandlerInfo(RefreshTokenCommandHandler)])

def register_auth_query_handlers(query_registry: QueryRegisty) -> None:
    """Register all query handlers with the query registry."""

    # Auth queries
    query_registry.register_query(GetByAcccessTokenQuery, QueryHandlerInfo(GetByAcccessTokenQueryHandler))


def register_auth_event_handlers(event_registry: EventRegisty) -> None:
    """Register all event handlers with the event registry."""

    # User events
    event_registry.subscribe(CreatedUserEvent, [
        EventHandlerInfo(SendVerifyEventHandler)
    ])
