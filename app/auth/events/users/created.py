from dataclasses import dataclass
from datetime import timedelta
import hashlib
import secrets

from app.auth.config import auth_config
from app.auth.emails.templates import VerifyTokenTemplate
from app.auth.exceptions import WrongDataException
from app.auth.models.user import CreatedUserEvent
from app.auth.repositories.session import TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.core.events.event import BaseEventHandler
from app.core.services.mail.service import BaseMailService, EmailData


@dataclass(frozen=True)
class SendVerifyEventHandler(BaseEventHandler[CreatedUserEvent, None]):
    user_repository: UserRepository
    mail_service: BaseMailService
    token_repository: TokenBlacklistRepository

    async def __call__(self, event: CreatedUserEvent) -> None:
        user = await self.user_repository.get_by_email(email=event.email)

        if not user:
            raise WrongDataException()

        reset_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()

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
