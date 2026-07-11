import hashlib
import secrets
from datetime import timedelta

import pytest
from dishka import AsyncContainer

from app.auth.commands.users.send_verify import SendVerifyCommand, SendVerifyCommandHandler
from app.auth.commands.users.verify import VerifyCommand, VerifyCommandHandler
from app.auth.exceptions import NotFoundUserError
from app.auth.models.user import User
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.core.services.auth.exceptions import InvalidTokenError
from tests.mocks import MockMailService


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestSendVerifyEmailCommand:
    @pytest.fixture
    async def handler(
        self,
        request_container: AsyncContainer
    ) -> SendVerifyCommandHandler:
        return await request_container.get(SendVerifyCommandHandler)

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

        with pytest.raises(NotFoundUserError):
            await handler.handle(command)


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestVerifyEmailCommand:
    @pytest.fixture
    async def handler(
        self,
        request_container: AsyncContainer,
    ) -> VerifyCommandHandler:
        return await request_container.get(VerifyCommandHandler)

    async def test_verify_email_success(
        self,
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

        verified_user = await user_repository.get_by_id(unverified_user.id)
        assert verified_user is not None
        assert verified_user.is_verified is True

    async def test_verify_email_invalid_token(
        self,
        handler: VerifyCommandHandler,
    ) -> None:
        command = VerifyCommand(token="invalid_token_123")

        with pytest.raises(InvalidTokenError):
            await handler.handle(command)

    async def test_verify_email_already_verified(
        self,
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

        verified_user = await user_repository.get_by_id(standard_user.id)
        assert verified_user is not None
        assert verified_user.is_verified is True
