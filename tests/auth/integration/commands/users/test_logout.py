import pytest
from dishka import AsyncContainer

from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.commands.auth.logout import LogoutCommand, LogoutCommandHandler
from app.auth.models.user import User
from app.auth.repositories.session import SessionRepository
from app.auth.services.jwt import AuthJWTManager
from app.core.services.auth.dto import JwtTokenType
from app.core.services.auth.exceptions import InvalidTokenError
from tests.auth.integration.factories import AuthCommandFactory


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestLogoutCommand:
    @pytest.fixture
    async def login_handler(
        self,
        request_container: AsyncContainer,
    ) -> LoginCommandHandler:
        return await request_container.get(LoginCommandHandler)

    @pytest.fixture
    async def logout_handler(
        self,
        request_container: AsyncContainer,
    ) -> LogoutCommandHandler:
        return await request_container.get(LogoutCommandHandler)

    async def test_logout_success(
        self,
        session_repository: SessionRepository,
        auth_jwt_manager: AuthJWTManager,
        login_handler: LoginCommandHandler,
        logout_handler: LogoutCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
        )
        login_command = LoginCommand(**cmd_data)
        token_group = await login_handler.handle(login_command)

        logout_command = LogoutCommand(refresh_token=token_group.refresh_token)
        await logout_handler.handle(logout_command)

        await auth_jwt_manager.validate_token(token_group.refresh_token, token_type=JwtTokenType.REFRESH)
        sessions = await session_repository.get_active_by_user(standard_user.id)
        active_sessions = [s for s in sessions if s.is_active]

        assert len(active_sessions) == 0

    async def test_logout_invalid_token(
        self,
        logout_handler: LogoutCommandHandler,
    ) -> None:
        logout_command = LogoutCommand(refresh_token="invalid_token")

        with pytest.raises(InvalidTokenError):
            await logout_handler.handle(logout_command)

    async def test_logout_none_token(
        self,
        logout_handler: LogoutCommandHandler,
    ) -> None:
        logout_command = LogoutCommand(refresh_token=None)

        with pytest.raises(InvalidTokenError):
            await logout_handler.handle(logout_command)
