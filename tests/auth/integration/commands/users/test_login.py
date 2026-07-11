from dishka import AsyncContainer
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.exceptions import WrongLoginDataError
from app.auth.models.user import User
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.session import SessionRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.device import generate_device_info
from app.auth.services.jwt import AuthJWTManager
from tests.auth.integration.factories import AuthCommandFactory, UserFactory


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestLoginCommand:
    @pytest.fixture
    async def handler(
        self,
        request_container: AsyncContainer,
    ) -> LoginCommandHandler:
        return await request_container.get(LoginCommandHandler)

    async def test_login_with_username_success(
        self,
        handler: LoginCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
            ip_address="127.0.0.1"
        )
        command = LoginCommand(**cmd_data)

        token_group = await handler.handle(command)

        assert token_group.access_token is not None
        assert token_group.refresh_token is not None

    async def test_login_with_email_success(
        self,
        handler: LoginCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.email,
            password="TestPass123!",
            ip_address="127.0.0.1"
        )
        command = LoginCommand(**cmd_data)

        token_group = await handler.handle(command)

        assert token_group.access_token is not None
        assert token_group.refresh_token is not None

    async def test_login_wrong_password(
        self,
        handler: LoginCommandHandler,
        standard_user: User,
    ) -> None:
        command = LoginCommand(
            username=standard_user.username,
            password="WrongPassword123!",
            user_agent="Mozilla/5.0",
            ip_address="1277.0.0.1"
        )

        with pytest.raises(WrongLoginDataError) as exc_info:
            await handler.handle(command)

        assert exc_info.value.username == standard_user.username

    async def test_login_nonexistent_user(
        self,
        handler: LoginCommandHandler,
    ) -> None:
        command = LoginCommand(
            username="nonexistent@example.com",
            password="TestPass123!",
            user_agent="Mozilla/5.0",
            ip_address="1277.0.0.1"
        )

        with pytest.raises(WrongLoginDataError):
            await handler.handle(command)

    async def test_login_creates_session(
        self,
        session_repository: SessionRepository,
        handler: LoginCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
            user_agent="Chrome/100.0",
            ip_address="127.0.0.1",
        )
        command = LoginCommand(**cmd_data)

        await handler.handle(command)

        sessions = await session_repository.get_active_by_user(standard_user.id)

        assert len(sessions) > 0
        assert any(s.user_agent == generate_device_info("Chrome/100.0").user_agent for s in sessions)

    async def test_login_multiple_times_same_device(
        self,
        session_repository: SessionRepository,
        handler: LoginCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
            user_agent="Chrome/100.0",
            ip_address="127.0.0.1"
        )
        command = LoginCommand(**cmd_data)

        token1 = await handler.handle(command)

        token2 = await handler.handle(command)

        assert token1.access_token != token2.access_token
        assert token1.refresh_token != token2.refresh_token

        sessions = await session_repository.get_active_by_user(standard_user.id)

        device_sessions = [s for s in sessions if "Chrome" in s.user_agent]
        assert len(device_sessions) == 1

    async def test_login_user_without_password(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        handler: LoginCommandHandler,
    ) -> None:
        role = await role_repository.get_with_permission_by_name("user")
        assert role is not None

        oauth_user = UserFactory.create_verified(
            email="oauth@example.com",
            username="oauthuser",
            password_hash=None,
            roles={role, },
        )
        await user_repository.create(oauth_user)
        await db_session.commit()

        command = LoginCommand(
            username="oauthuser",
            password="AnyPassword123!",
            user_agent="Mozilla/5.0",
            ip_address="1277.0.0.1"
        )

        with pytest.raises(WrongLoginDataError):
            await handler.handle(command)

    async def test_login_tokens_contain_user_data(
        self,
        handler: LoginCommandHandler,
        auth_jwt_manager: AuthJWTManager,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
            ip_address="127.0.0.1",
        )
        command = LoginCommand(**cmd_data)

        token_group = await handler.handle(command)
        token_data = await auth_jwt_manager.validate_token(token_group.access_token)
        assert token_data.sub == str(standard_user.id)
        assert "user" in token_data.roles
        assert token_data.did is not None
