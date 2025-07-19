from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.auth.login import LoginCommandHandler
from app.auth.commands.auth.logout import LogoutCommandHandler
from app.auth.commands.auth.refresh_token import RefreshTokenCommandHandler
from app.auth.commands.users.register import RegisterCommandHandler
from app.auth.commands.users.reset_password import ResetPasswordCommandHandler
from app.auth.commands.users.send_reset_password import SendResetPasswordCommandHandler
from app.auth.commands.users.send_verify import SendVerifyCommandHandler
from app.auth.commands.users.verify import VerifyCommandHandler

from app.auth.repositories.user import UserRepository
from app.auth.repositories.token import TokenRepository
from app.core.services.mail.service import MailServiceInterface
from app.core.events.service import BaseEventBus


class HandlersProvider(Provider):
    scope = Scope.REQUEST

    # Auth Command Handlers
    @provide
    def get_login_command_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        token_repository: TokenRepository,
    ) -> LoginCommandHandler:
        return LoginCommandHandler(
            session=session,
            user_repository=user_repository,
            token_repository=token_repository,
        )

    @provide
    def get_logout_command_handler(
        self,
        session: AsyncSession,
        token_repository: TokenRepository,
    ) -> LogoutCommandHandler:
        return LogoutCommandHandler(
            session=session,
            token_repository=token_repository,
        )

    @provide
    def get_refresh_token_command_handler(
        self,
        session: AsyncSession,
        token_repository: TokenRepository,
    ) -> RefreshTokenCommandHandler:
        return RefreshTokenCommandHandler(
            session=session,
            token_repository=token_repository,
        )

    # User Command Handlers
    @provide
    def get_register_command_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        event_bus: BaseEventBus,
    ) -> RegisterCommandHandler:
        return RegisterCommandHandler(
            session=session,
            user_repository=user_repository,
            event_bus=event_bus,
        )

    @provide
    def get_send_verify_command_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        mail_service: MailServiceInterface,
    ) -> SendVerifyCommandHandler:
        return SendVerifyCommandHandler(
            session=session,
            user_repository=user_repository,
            mail_service=mail_service,
        )

    @provide
    def get_verify_command_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> VerifyCommandHandler:
        return VerifyCommandHandler(
            session=session,
            user_repository=user_repository,
        )

    @provide
    def get_send_reset_password_command_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        mail_service: MailServiceInterface,
    ) -> SendResetPasswordCommandHandler:
        return SendResetPasswordCommandHandler(
            session=session,
            user_repository=user_repository,
            mail_service=mail_service,
        )

    @provide
    def get_reset_password_command_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> ResetPasswordCommandHandler:
        return ResetPasswordCommandHandler(
            session=session,
            user_repository=user_repository,
        )