import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.exceptions import WrongLoginDataException
from app.auth.models.user import User
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.session import SessionRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.device import generate_device_info
from app.auth.services.hash import HashService
from app.auth.services.jwt import AuthJWTManager
from app.auth.services.session import SessionManager
from tests.auth.integration.factories import AuthCommandFactory, UserFactory


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestLoginCommand:
    @pytest.fixture
    def handler(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        session_manager: SessionManager,
        auth_jwt_manager: AuthJWTManager,
        hash_service: HashService,
    ) -> LoginCommandHandler:
        return LoginCommandHandler(
            session=db_session,
            user_repository=user_repository,
            session_manager=session_manager,
            jwt_manager=auth_jwt_manager,
            hash_service=hash_service,
        )

    async def test_login_with_username_success(
        self,
        handler: LoginCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
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
        )

        with pytest.raises(WrongLoginDataException) as exc_info:
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
        )

        with pytest.raises(WrongLoginDataException):
            await handler.handle(command)

    async def test_login_creates_session(
        self,
        db_session: AsyncSession,
        session_repository: SessionRepository,
        handler: LoginCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
            user_agent="Chrome/100.0",
        )
        command = LoginCommand(**cmd_data)

        await handler.handle(command)
        await db_session.commit()

        sessions = await session_repository.get_active_by_user(standard_user.id)

        assert len(sessions) > 0
        assert any(s.user_agent == generate_device_info("Chrome/100.0").user_agent for s in sessions)

    async def test_login_multiple_times_same_device(
        self,
        db_session: AsyncSession,
        session_repository: SessionRepository,
        handler: LoginCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
            user_agent="Chrome/100.0",
        )
        command = LoginCommand(**cmd_data)

        token1 = await handler.handle(command)
        await db_session.commit()

        token2 = await handler.handle(command)
        await db_session.commit()

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
        )

        with pytest.raises(WrongLoginDataException):
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
        )
        command = LoginCommand(**cmd_data)

        token_group = await handler.handle(command)
        token_data = await auth_jwt_manager.validate_token(token_group.access_token)
        assert token_data.sub == str(standard_user.id)
        assert "user" in token_data.roles
        assert token_data.did is not None
