from dishka import Provider, Scope, provide

from app.auth.commands.auth.login import LoginCommandHandler
from app.auth.commands.auth.logout import LogoutCommandHandler
from app.auth.commands.auth.refresh_token import RefreshTokenCommandHandler
from app.auth.commands.users.register import RegisterCommandHandler
from app.auth.commands.users.reset_password import ResetPasswordCommandHandler
from app.auth.commands.users.send_reset_password import SendResetPasswordCommandHandler
from app.auth.commands.users.send_verify import SendVerifyCommandHandler
from app.auth.commands.users.verify import VerifyCommandHandler


class AuthCommandProvider(Provider):
    scope = Scope.REQUEST

    register_handler = provide(RegisterCommandHandler)
    reset_password_handler = provide(ResetPasswordCommandHandler)
    send_reset_password_handler = provide(SendResetPasswordCommandHandler)
    send_verify_handler = provide(SendVerifyCommandHandler)
    verify_handler = provide(VerifyCommandHandler)

    login_handler = provide(LoginCommandHandler)
    logout_handler = provide(LogoutCommandHandler)
    refresh_handler = provide(RefreshTokenCommandHandler)
