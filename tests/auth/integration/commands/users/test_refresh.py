import asyncio

from dishka import AsyncContainer
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.commands.auth.refresh_token import RefreshTokenCommand, RefreshTokenCommandHandler
from app.auth.exceptions import NotFoundOrInactiveSessionError
from app.auth.models.user import User
from app.auth.repositories.session import SessionRepository
from app.auth.services.jwt import AuthJWTManager
from app.core.services.auth.dto import JwtTokenType
from app.core.services.auth.exceptions import InvalidTokenError
from tests.auth.integration.factories import AuthCommandFactory


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestRefreshTokenCommand:
    @pytest.fixture
    async def login_handler(
        self,
        request_container: AsyncContainer,
    ) -> LoginCommandHandler:
        return await request_container.get(LoginCommandHandler)

    @pytest.fixture
    async def refresh_handler(
        self,
        request_container: AsyncContainer,
    ) -> RefreshTokenCommandHandler:
        return await request_container.get(RefreshTokenCommandHandler)

    async def test_refresh_token_success(
        self,
        auth_jwt_manager: AuthJWTManager,
        login_handler: LoginCommandHandler,
        refresh_handler: RefreshTokenCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
        )
        login_command = LoginCommand(**cmd_data)
        old_tokens = await login_handler.handle(login_command)

        refresh_command = RefreshTokenCommand(
            refresh_token=old_tokens.refresh_token,
        )
        new_tokens = await refresh_handler.handle(refresh_command)

        assert new_tokens.access_token != old_tokens.access_token
        assert new_tokens.refresh_token != old_tokens.refresh_token

        new_token_data = await auth_jwt_manager.validate_token(new_tokens.access_token)
        assert new_token_data.sub == str(standard_user.id)

    async def test_refresh_token_invalid_token(
        self,
        refresh_handler: RefreshTokenCommandHandler,
    ) -> None:
        refresh_command = RefreshTokenCommand(
            refresh_token="invalid_token",
        )

        with pytest.raises(InvalidTokenError):
            await refresh_handler.handle(refresh_command)

    async def test_refresh_token_inactive_session(
        self,
        db_session: AsyncSession,
        auth_jwt_manager: AuthJWTManager,
        session_repository: SessionRepository,
        login_handler: LoginCommandHandler,
        refresh_handler: RefreshTokenCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
        )
        login_command = LoginCommand(**cmd_data)
        tokens = await login_handler.handle(login_command)

        token_data = await auth_jwt_manager.validate_token(tokens.refresh_token, token_type=JwtTokenType.REFRESH)
        await session_repository.deactivate_user_session(
            user_id=int(token_data.sub),
            device_id=token_data.did,
        )
        await db_session.commit()

        refresh_command = RefreshTokenCommand(
            refresh_token=tokens.refresh_token,
        )

        with pytest.raises(NotFoundOrInactiveSessionError):
            await refresh_handler.handle(refresh_command)

    async def test_refresh_token_updates_session_activity(
        self,
        auth_jwt_manager: AuthJWTManager,
        session_repository: SessionRepository,
        login_handler: LoginCommandHandler,
        refresh_handler: RefreshTokenCommandHandler,
        standard_user: User,
    ) -> None:
        cmd_data = AuthCommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!",
        )
        login_command = LoginCommand(**cmd_data)
        tokens = await login_handler.handle(login_command)

        token_data = await auth_jwt_manager.validate_token(tokens.refresh_token, token_type=JwtTokenType.REFRESH)
        old_session = await session_repository.get_active_by_device(
            user_id=int(token_data.sub),
            device_id=token_data.did,
        )

        assert old_session is not None
        old_activity = old_session.last_activity

        await asyncio.sleep(0.1)

        refresh_command = RefreshTokenCommand(
            refresh_token=tokens.refresh_token,
        )
        await refresh_handler.handle(refresh_command)

        new_session = await session_repository.get_active_by_device(
            user_id=int(token_data.sub),
            device_id=token_data.did,
        )

        assert new_session is not None
        assert new_session.last_activity > old_activity
