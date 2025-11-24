import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import timedelta

from app.auth.config import auth_config
from app.auth.emails.templates import ResetTokenTemplate
from app.auth.exceptions import NotFoundUserException
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.configs.app import app_config
from app.core.services.mail.service import BaseMailService, EmailData

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class SendResetPasswordCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class SendResetPasswordCommandHandler(BaseCommandHandler[SendResetPasswordCommand, None]):
    user_repository: UserRepository
    mail_service: BaseMailService
    token_repository: TokenBlacklistRepository

    async def handle(self, command: SendResetPasswordCommand) -> None:
        user = await self.user_repository.get_by_email(email=command.email)
        if not user:
            raise NotFoundUserException(user_by=command.email, user_field="email")

        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

        await self.token_repository.add_token(
            hashed_token,
            user_id=user.id,
            expiration=timedelta(minutes=auth_config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES)
        )

        email_data = EmailData(subject="Password reset code", recipient=user.email)
        template = ResetTokenTemplate(
            username=user.username,
            link=f"{app_config.app_url}/reset_password?token={hashed_token}",
            token=hashed_token,
            valid_minutes=auth_config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES,
        )
        await self.mail_service.queue(template=template, email_data=email_data)
        logger.info("Send password reset email", extra={"email": user.email})
