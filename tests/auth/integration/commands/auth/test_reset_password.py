import hashlib
import secrets
from datetime import timedelta

import pytest
from dishka import AsyncContainer

from app.auth.commands.users.reset_password import ResetPasswordCommand, ResetPasswordCommandHandler
from app.auth.commands.users.send_reset_password import SendResetPasswordCommand, SendResetPasswordCommandHandler
from app.auth.exceptions import NotFoundUserError, PasswordMismatchError
from app.auth.models.user import User
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.hash import HashService
from app.core.services.auth.exceptions import InvalidTokenError
from tests.conftest import MockMailService


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestSendResetPasswordCommand:
    @pytest.fixture
    async def handler(
        self,
        request_container: AsyncContainer
    ) -> SendResetPasswordCommandHandler:
        return await request_container.get(SendResetPasswordCommandHandler)


    async def test_send_reset_password_code_success(
        self,
        standard_user: User,
        mock_mail_service: MockMailService,
        handler: SendResetPasswordCommandHandler,
    ) -> None:
        command = SendResetPasswordCommand(email=standard_user.email)
        await handler.handle(command)

        assert len(mock_mail_service.sent_emails) == 1
        assert mock_mail_service.sent_emails[0]["data"].recipient == standard_user.email

    async def test_send_reset_password_nonexistent_user(
        self,
        handler: SendResetPasswordCommandHandler,
    ) -> None:
        command = SendResetPasswordCommand(email="nonexistent@example.com")

        with pytest.raises(NotFoundUserError):
            await handler.handle(command)


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestResetPasswordCommand:
    @pytest.fixture
    async def handler(
        self,
        request_container: AsyncContainer
    ) -> ResetPasswordCommandHandler:
        return await request_container.get(ResetPasswordCommandHandler)

    async def test_reset_password_success(
        self,
        user_repository: UserRepository,
        hash_service: HashService,
        standard_user: User,
        token_blacklist_repository: TokenBlacklistRepository,
        handler: ResetPasswordCommandHandler,
    ) -> None:
        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

        await token_blacklist_repository.add_token(
            hashed_token,
            user_id=standard_user.id,
            expiration=timedelta(minutes=15),
        )

        new_password = "NewPassword123!"
        command = ResetPasswordCommand(
            token=hashed_token,
            password=new_password,
            password_repeat=new_password,
        )

        await handler.handle(command)

        updated_user = await user_repository.get_by_id(standard_user.id)
        assert updated_user is not None
        assert updated_user.password_hash is not None
        assert hash_service.verify_password(new_password, updated_user.password_hash)

    async def test_reset_password_invalid_token(
        self,
        handler: ResetPasswordCommandHandler,
    ) -> None:
        command = ResetPasswordCommand(
            token="invalid_token",
            password="NewPassword123!",
            password_repeat="NewPassword123!",
        )

        with pytest.raises(InvalidTokenError):
            await handler.handle(command)

    async def test_reset_password_mismatch(
        self,
        standard_user: User,
        token_blacklist_repository: TokenBlacklistRepository,
        handler: ResetPasswordCommandHandler,
    ) -> None:
        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

        await token_blacklist_repository.add_token(
            hashed_token,
            user_id=standard_user.id,
            expiration=timedelta(minutes=15),
        )

        command = ResetPasswordCommand(
            token=hashed_token,
            password="NewPassword123!",
            password_repeat="DifferentPassword123!",
        )

        with pytest.raises(PasswordMismatchError):
            await handler.handle(command)

    async def test_reset_password_token_invalidated_after_use(
        self,
        standard_user: User,
        token_blacklist_repository: TokenBlacklistRepository,
        handler: ResetPasswordCommandHandler,
    ) -> None:
        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

        await token_blacklist_repository.add_token(
            hashed_token,
            user_id=standard_user.id,
            expiration=timedelta(minutes=15),
        )

        new_password = "NewPassword123!"
        command = ResetPasswordCommand(
            token=hashed_token,
            password=new_password,
            password_repeat=new_password,
        )

        await handler.handle(command)

        with pytest.raises(InvalidTokenError):
            await handler.handle(command)
