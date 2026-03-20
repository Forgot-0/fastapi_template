import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.auth.logout import LogoutCommand, LogoutCommandHandler
from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.models.user import User
from app.auth.repositories.session import SessionRepository, TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.hash import HashService
from app.auth.services.jwt import AuthJWTManager
from app.auth.services.session import SessionManager
from app.core.services.auth.dto import JwtTokenType
from app.core.services.auth.exceptions import InvalidTokenException
from tests.auth.integration.factories import CommandFactory


@pytest.mark.integration
@pytest.mark.auth
class TestLogoutCommand:

    @pytest.fixture
    def handler(
        self,
        db_session: AsyncSession,
        session_manager: SessionManager,
        jwt_manager: AuthJWTManager,
        session_repository: SessionRepository,
        token_blacklist_repository: TokenBlacklistRepository
    ) -> LogoutCommandHandler:
        return LogoutCommandHandler(
            session=db_session,
            session_manager=session_manager,
            jwt_manager=jwt_manager,
            session_repository=session_repository,
            token_blacklist=token_blacklist_repository,
        )

    @pytest.mark.asyncio
    async def test_logout_success(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        session_manager: SessionManager,
        jwt_manager: AuthJWTManager,
        hash_service: HashService,
        standard_user: User,
        handler
    ):
        login_handler = LoginCommandHandler(
            session=db_session,
            user_repository=user_repository,
            session_manager=session_manager,
            jwt_manager=jwt_manager,
            hash_service=hash_service,
        )

        cmd_data = CommandFactory.create_login_command(
            username=standard_user.username,
            password="TestPass123!"
        )
        login_command = LoginCommand(**cmd_data)
        token_group = await login_handler.handle(login_command)
        await db_session.commit()

        session_repo = SessionRepository(session=db_session)

        logout_command = LogoutCommand(refresh_token=token_group.refresh_token)
        await handler.handle(logout_command)
        await db_session.commit()

        token_data = await jwt_manager.validate_token(token_group.refresh_token, token_type=JwtTokenType.REFRESH)
        sessions = await session_repo.get_active_by_user(standard_user.id)
        active_sessions = [s for s in sessions if s.is_active]

        assert len(active_sessions) == 0

    @pytest.mark.asyncio
    async def test_logout_invalid_token(
        self,
        handler
    ) -> None:
        logout_command = LogoutCommand(refresh_token="invalid_token")

        with pytest.raises(InvalidTokenException):
            await handler.handle(logout_command)

    @pytest.mark.asyncio
    async def test_logout_none_token(
        self,
        handler
    ) -> None:

        logout_command = LogoutCommand(refresh_token=None)

        with pytest.raises(InvalidTokenException):
            await handler.handle(logout_command)

