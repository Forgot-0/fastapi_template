import hashlib
import secrets
from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.commands.users.send_verify import SendVerifyCommand, SendVerifyCommandHandler
from app.auth.commands.users.verify import VerifyCommand, VerifyCommandHandler
from app.auth.exceptions import NotFoundUserException
from app.auth.models.user import User
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.core.services.auth.exceptions import InvalidTokenException
from tests.conftest import MockEventBus, MockMailService


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestSendVerifyEmailCommand:
    @pytest.fixture
    def handler(
        self,
        user_repository: UserRepository,
        mock_mail_service: MockMailService,
        token_blacklist_repository: TokenBlacklistRepository,
    ) -> SendVerifyCommandHandler:
        return SendVerifyCommandHandler(
            user_repository=user_repository,
            mail_service=mock_mail_service,
            token_repository=token_blacklist_repository,
        )

    async def test_send_verify_email_success(
        self,
        unverified_user: User,
        mock_mail_service: MockMailService,
        handler: SendVerifyCommandHandler,
    ) -> None:
        command = SendVerifyCommand(email=unverified_user.email)
        await handler.handle(command)

        assert len(mock_mail_service.sent_emails) == 1
        assert mock_mail_service.sent_emails[0]["data"].recipient == unverified_user.email

    async def test_send_verify_email_nonexistent_user(
        self,
        handler: SendVerifyCommandHandler,
    ) -> None:
        command = SendVerifyCommand(email="nonexistent@example.com")

        with pytest.raises(NotFoundUserException):
            await handler.handle(command)


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestVerifyEmailCommand:
    @pytest.fixture
    def handler(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        mock_event_bus: MockEventBus,
        token_blacklist_repository: TokenBlacklistRepository,
    ) -> VerifyCommandHandler:
        return VerifyCommandHandler(
            session=db_session,
            event_bus=mock_event_bus,
            user_repository=user_repository,
            token_repository=token_blacklist_repository,
        )

    async def test_verify_email_success(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        unverified_user: User,
        token_blacklist_repository: TokenBlacklistRepository,
        handler: VerifyCommandHandler,
    ) -> None:
        verify_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(verify_token.encode()).hexdigest()

        await token_blacklist_repository.add_token(
            hashed_token,
            user_id=unverified_user.id,
            expiration=timedelta(minutes=15),
        )

        command = VerifyCommand(token=hashed_token)
        await handler.handle(command)
        await db_session.commit()

        verified_user = await user_repository.get_by_id(unverified_user.id)
        assert verified_user is not None
        assert verified_user.is_verified is True

    async def test_verify_email_invalid_token(
        self,
        handler: VerifyCommandHandler,
    ) -> None:
        command = VerifyCommand(token="invalid_token_123")

        with pytest.raises(InvalidTokenException):
            await handler.handle(command)

    async def test_verify_email_already_verified(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        standard_user: User,
        token_blacklist_repository: TokenBlacklistRepository,
        handler: VerifyCommandHandler,
    ) -> None:
        verify_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(verify_token.encode()).hexdigest()

        await token_blacklist_repository.add_token(
            hashed_token,
            user_id=standard_user.id,
            expiration=timedelta(minutes=15),
        )

        command = VerifyCommand(token=hashed_token)
        await handler.handle(command)
        await db_session.commit()

        verified_user = await user_repository.get_by_id(standard_user.id)
        assert verified_user is not None
        assert verified_user.is_verified is True
