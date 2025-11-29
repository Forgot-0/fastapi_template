import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.auth.refresh_token import RefreshTokenCommand, RefreshTokenCommandHandler
from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler
from app.auth.exceptions import InvalidTokenException, NotFoundOrInactiveSessionException
from app.auth.models.user import User
from app.auth.repositories.session import SessionRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.tokens import TokenType
from app.auth.schemas.user import UserJWTData
from app.auth.services.hash import HashService
from app.auth.services.jwt import JWTManager
from app.auth.services.session import SessionManager
from tests.auth.integration.factories import CommandFactory


@pytest.mark.integration
@pytest.mark.auth
class TestRefreshTokenCommand:

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        session_repository: SessionRepository,
        session_manager: SessionManager,
        jwt_manager: JWTManager,
        hash_service: HashService,
        standard_user: User,
    ) -> None:
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
        old_tokens = await login_handler.handle(login_command)
        await db_session.commit()

        old_token_data = await jwt_manager.validate_token(old_tokens.access_token)
        user_jwt_data = UserJWTData.create_from_token(old_token_data)

        refresh_handler = RefreshTokenCommandHandler(
            session=db_session,
            jwt_manager=jwt_manager,
            session_repository=session_repository,
        )

        refresh_command = RefreshTokenCommand(
            refresh_token=old_tokens.refresh_token,
            user_jwt_data=user_jwt_data
        )
        new_tokens = await refresh_handler.handle(refresh_command)

        assert new_tokens.access_token != old_tokens.access_token
        assert new_tokens.refresh_token != old_tokens.refresh_token

        new_token_data = await jwt_manager.validate_token(new_tokens.access_token)
        assert new_token_data.sub == str(standard_user.id)
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid_token(
        self,
        db_session: AsyncSession,
        jwt_manager: JWTManager,
        session_repository: SessionRepository,
        standard_user: User,
    ) -> None:
        refresh_handler = RefreshTokenCommandHandler(
            session=db_session,
            jwt_manager=jwt_manager,
            session_repository=session_repository,
        )

        user_jwt_data = UserJWTData(
            id=str(standard_user.id),
            roles=["user"],
            permissions=[],
            security_level=1,
            device_id="test_device"
        )

        refresh_command = RefreshTokenCommand(
            refresh_token="invalid_token",
            user_jwt_data=user_jwt_data
        )

        with pytest.raises(InvalidTokenException):
            await refresh_handler.handle(refresh_command)

    @pytest.mark.asyncio
    async def test_refresh_token_inactive_session(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        session_manager: SessionManager,
        jwt_manager: JWTManager,
        hash_service: HashService,
        session_repository: SessionRepository,
        standard_user: User,
    ) -> None:

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
        tokens = await login_handler.handle(login_command)
        await db_session.commit()

        token_data = await jwt_manager.validate_token(tokens.refresh_token, token_type=TokenType.REFRESH)
        await session_repository.deactivate_user_session(
            user_id=int(token_data.sub),
            device_id=token_data.did
        )
        await db_session.commit()

        user_jwt_data = UserJWTData.create_from_token(token_data)
        refresh_handler = RefreshTokenCommandHandler(
            session=db_session,
            jwt_manager=jwt_manager,
            session_repository=session_repository,
        )

        refresh_command = RefreshTokenCommand(
            refresh_token=tokens.refresh_token,
            user_jwt_data=user_jwt_data
        )

        with pytest.raises(NotFoundOrInactiveSessionException):
            await refresh_handler.handle(refresh_command)

    @pytest.mark.asyncio
    async def test_refresh_token_updates_session_activity(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        session_manager: SessionManager,
        jwt_manager: JWTManager,
        hash_service: HashService,
        standard_user: User,
    ) -> None:
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
        tokens = await login_handler.handle(login_command)
        await db_session.commit()

        session_repo = SessionRepository(session=db_session)
        token_data = await jwt_manager.validate_token(tokens.refresh_token, token_type=TokenType.REFRESH)
        old_session = await session_repo.get_active_by_device(
            user_id=int(token_data.sub),
            device_id=token_data.did
        )

        assert old_session is not None
        old_activity = old_session.last_activity

        import asyncio
        await asyncio.sleep(0.1)

        user_jwt_data = UserJWTData.create_from_token(token_data)
        refresh_handler = RefreshTokenCommandHandler(
            session=db_session,
            jwt_manager=jwt_manager,
            session_repository=session_repo,
        )

        refresh_command = RefreshTokenCommand(
            refresh_token=tokens.refresh_token,
            user_jwt_data=user_jwt_data
        )
        await refresh_handler.handle(refresh_command)
        await db_session.commit()

        new_session = await session_repo.get_active_by_device(
            user_id=int(token_data.sub),
            device_id=token_data.did
        )

        assert new_session is not None
        assert new_session.last_activity > old_activity