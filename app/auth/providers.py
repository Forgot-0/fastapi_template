from dishka import Provider, Scope, decorate, provide

from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.commands.auth.logout import LogoutCommand, LogoutCommandHandler
from app.auth.commands.auth.refresh_token import RefreshTokenCommand, RefreshTokenCommandHandler
from app.auth.commands.users.register import RegisterCommand, RegisterCommandHandler
from app.auth.commands.users.reset_password import ResetPasswordCommand, ResetPasswordCommandHandler
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand, SendResetPasswordCommandHandler
from app.auth.commands.users.send_verify import SendVerifyCommand, SendVerifyCommandHandler
from app.auth.commands.users.verify import VerifyCommand, VerifyCommandHandler
from app.auth.events.users.created import SendVerifyEventHandler
from app.auth.models.user import CreatedUserEvent
from app.auth.queries.auth.get_by_token import GetByAccessTokenQuery, GetByAccessTokenQueryHandler
from app.auth.repositories.token import TokenRepository
from app.auth.repositories.user import UserRepository
from app.core.events.event import EventRegisty
from app.core.mediators.command import CommandRegisty
from app.core.mediators.query import QueryRegistry


class AuthModuleProvider(Provider):
    scope = Scope.REQUEST

    # repository
    user_repository = provide(UserRepository)
    token_repository = provide(TokenRepository)

    #handelr command
    register_handler = provide(RegisterCommandHandler)
    reset_password_handler = provide(ResetPasswordCommandHandler)
    send_reset_password_handler = provide(SendResetPasswordCommandHandler)
    send_verify_handler = provide(SendVerifyCommandHandler)
    verify_handler = provide(VerifyCommandHandler)

    login_handler = provide(LoginCommandHandler)
    logout_handler = provide(LogoutCommandHandler)
    refresh_handler = provide(RefreshTokenCommandHandler)

    @decorate
    def register_auth_command_handlers(self, command_registry: CommandRegisty) -> CommandRegisty:
        # User commands
        command_registry.register_command(RegisterCommand, [RegisterCommandHandler])
        command_registry.register_command(VerifyCommand, [VerifyCommandHandler])
        command_registry.register_command(SendVerifyCommand, [SendVerifyCommandHandler])
        command_registry.register_command(ResetPasswordCommand, [ResetPasswordCommandHandler])
        command_registry.register_command(SendResetPasswordCommand, [SendResetPasswordCommandHandler])

        # Auth commands
        command_registry.register_command(LoginCommand, [LoginCommandHandler])
        command_registry.register_command(LogoutCommand, [LogoutCommandHandler])
        command_registry.register_command(RefreshTokenCommand, [RefreshTokenCommandHandler])
        return command_registry

    #event
    send_verify_email = provide(SendVerifyEventHandler)

    @decorate
    def register_auth_event_handlers(self, event_registry: EventRegisty) -> EventRegisty:
        # User events
        event_registry.subscribe(CreatedUserEvent, [
            SendVerifyEventHandler
        ])
        return event_registry

    # query
    get_user_by_access_token_query_handler = provide(GetByAccessTokenQueryHandler)

    def register_auth_query_handlers(self, query_registry: QueryRegistry) -> QueryRegistry:
        # Auth queries
        query_registry.register_query(GetByAccessTokenQuery, GetByAccessTokenQueryHandler)
        return query_registry
