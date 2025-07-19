from dishka import Provider, provide, Scope, Container

from app.core.mediators.imediator import DishkaMediator
from app.core.mediators.command import CommandRegisty, CommandHandlerRegistry
from app.core.mediators.query import QueryRegisty, QueryHandleRegistry

# Import all commands
from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.commands.auth.logout import LogoutCommand, LogoutCommandHandler
from app.auth.commands.auth.refresh_token import RefreshTokenCommand, RefreshTokenCommandHandler
from app.auth.commands.users.register import RegisterCommand, RegisterCommandHandler
from app.auth.commands.users.reset_password import ResetPasswordCommand, ResetPasswordCommandHandler
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand, SendResetPasswordCommandHandler
from app.auth.commands.users.send_verify import SendVerifyCommand, SendVerifyCommandHandler
from app.auth.commands.users.verify import VerifyCommand, VerifyCommandHandler


class MediatorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_command_registry(self) -> CommandRegisty:
        registry = CommandRegisty()
        
        # Register all command handlers
        registry.register_command(
            LoginCommand,
            [CommandHandlerRegistry(handler_type=LoginCommandHandler)]
        )
        registry.register_command(
            LogoutCommand,
            [CommandHandlerRegistry(handler_type=LogoutCommandHandler)]
        )
        registry.register_command(
            RefreshTokenCommand,
            [CommandHandlerRegistry(handler_type=RefreshTokenCommandHandler)]
        )
        registry.register_command(
            RegisterCommand,
            [CommandHandlerRegistry(handler_type=RegisterCommandHandler)]
        )
        registry.register_command(
            SendVerifyCommand,
            [CommandHandlerRegistry(handler_type=SendVerifyCommandHandler)]
        )
        registry.register_command(
            VerifyCommand,
            [CommandHandlerRegistry(handler_type=VerifyCommandHandler)]
        )
        registry.register_command(
            SendResetPasswordCommand,
            [CommandHandlerRegistry(handler_type=SendResetPasswordCommandHandler)]
        )
        registry.register_command(
            ResetPasswordCommand,
            [CommandHandlerRegistry(handler_type=ResetPasswordCommandHandler)]
        )
        
        return registry

    @provide
    def get_query_registry(self) -> QueryRegisty:
        registry = QueryRegisty()
        # Add query handlers here when they exist
        return registry

    @provide
    def get_mediator(
        self,
        container: Container,
        command_registry: CommandRegisty,
        query_registry: QueryRegisty,
    ) -> DishkaMediator:
        return DishkaMediator(
            container=container,
            command_registy=command_registry,
            query_registy=query_registry,
        )