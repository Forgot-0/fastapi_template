import hashlib
import secrets
from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.users.reset_password import ResetPasswordCommand, ResetPasswordCommandHandler
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand, SendResetPasswordCommandHandler
from app.auth.exceptions import InvalidTokenException, NotFoundUserException, PasswordMismatchException
from app.auth.models.user import User
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.hash import HashService
from tests.conftest import MockEventBus, MockMailService


@pytest.mark.integration
@pytest.mark.auth
class TestResetPasswordCommand:

    @pytest.mark.asyncio
    async def test_send_reset_password_code_success(
        self,
        user_repository: UserRepository,
        standard_user: User,
        token_blacklist_repository: TokenBlacklistRepository,
        mock_mail_service: MockMailService
    ) -> None:
        handler = SendResetPasswordCommandHandler(
            user_repository=user_repository,
            mail_service=mock_mail_service,
            token_repository=token_blacklist_repository,
        )

        command = SendResetPasswordCommand(email=standard_user.email)
        await handler.handle(command)

        assert len(mock_mail_service.sent_emails) == 1
        assert mock_mail_service.sent_emails[0]["data"].recipient == standard_user.email

    @pytest.mark.asyncio
    async def test_send_reset_password_nonexistent_user(
        self,
        user_repository: UserRepository,
        mock_mail_service: MockMailService,
        token_blacklist_repository: TokenBlacklistRepository,
    ) -> None:

        handler = SendResetPasswordCommandHandler(
            user_repository=user_repository,
            mail_service=mock_mail_service,
            token_repository=token_blacklist_repository,
        )

        command = SendResetPasswordCommand(email="nonexistent@example.com")

        with pytest.raises(NotFoundUserException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_reset_password_success(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        hash_service: HashService,
        standard_user: User,
        mock_event_bus: MockEventBus,
        token_blacklist_repository: TokenBlacklistRepository,
    ) -> None:
        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

        await token_blacklist_repository.add_token(
            hashed_token,
            user_id=standard_user.id,
            expiration=timedelta(minutes=15)
        )

        handler = ResetPasswordCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            token_repository=token_blacklist_repository,
            hash_service=hash_service,
        )

        new_password = "NewPassword123!"
        command = ResetPasswordCommand(
            token=hashed_token,
            password=new_password,
            repeat_password=new_password,
        )

        await handler.handle(command)
        await db_session.commit()

        updated_user = await user_repository.get_by_id(standard_user.id)
        assert updated_user is not None
        assert updated_user.password_hash is not None
        assert hash_service.verify_password(new_password, updated_user.password_hash)
    
    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        hash_service: HashService,
        mock_event_bus: MockEventBus,
        token_blacklist_repository: TokenBlacklistRepository,
    ) -> None:

        handler = ResetPasswordCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            token_repository=token_blacklist_repository,
            hash_service=hash_service,
        )

        command = ResetPasswordCommand(
            token="invalid_token",
            password="NewPassword123!",
            repeat_password="NewPassword123!",
        )

        with pytest.raises(InvalidTokenException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_reset_password_mismatch(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        hash_service: HashService,
        standard_user: User,
        mock_event_bus: MockEventBus,
        token_blacklist_repository: TokenBlacklistRepository,
    ) -> None:
        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

        await token_blacklist_repository.add_token(
            hashed_token,
            user_id=standard_user.id,
            expiration=timedelta(minutes=15)
        )

        handler = ResetPasswordCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            token_repository=token_blacklist_repository,
            hash_service=hash_service,
        )

        command = ResetPasswordCommand(
            token=hashed_token,
            password="NewPassword123!",
            repeat_password="DifferentPassword123!",
        )

        with pytest.raises(PasswordMismatchException):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_reset_password_token_invalidated_after_use(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        hash_service: HashService,
        standard_user: User,
        mock_event_bus: MockEventBus,
        token_blacklist_repository: TokenBlacklistRepository
    ) -> None:
        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

        await token_blacklist_repository.add_token(
            hashed_token,
            user_id=standard_user.id,
            expiration=timedelta(minutes=15)
        )

        handler = ResetPasswordCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            token_repository=token_blacklist_repository,
            hash_service=hash_service,
        )

        new_password = "NewPassword123!"
        command = ResetPasswordCommand(
            token=hashed_token,
            password=new_password,
            repeat_password=new_password,
        )

        await handler.handle(command)
        await db_session.commit()

        with pytest.raises(InvalidTokenException):
            await handler.handle(command)
