from dataclasses import dataclass
from datetime import timedelta
import hashlib
import logging
import secrets

from app.auth.config import auth_config
from app.auth.emails.templates import VerifyTokenTemplate
from app.auth.exceptions import WrongDataException
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.services.mail.service import BaseMailService, EmailData


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class SendVerifyCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class SendVerifyCommandHandler(BaseCommandHandler[SendVerifyCommand, None]):
    user_repository: UserRepository
    mail_service: BaseMailService
    token_repository: TokenBlacklistRepository


    async def handle(self, command: SendVerifyCommand) -> None:
        user = await self.user_repository.get_by_email(email=command.email)

        if not user:
            raise WrongDataException()

        verify_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(verify_token.encode()).hexdigest()
        await self.token_repository.add_token(
            hashed_token,
            user_id=user.id,
            expiration=timedelta(minutes=auth_config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES)
        )

        email_data = EmailData(subject="Код для верификации почты", recipient=user.email)
        template = VerifyTokenTemplate(
            email=user.email,
            token=hashed_token,
        )
        await self.mail_service.queue(template=template, email_data=email_data)
        logger.info("Send verify email", extra={"email": user.email})
