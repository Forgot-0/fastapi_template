from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import generate_verify_token
from app.core.configs.app import app_config
from app.auth.config import auth_config
from app.auth.emails.templates import VerifyTokenTemplate
from app.auth.repositories.user import UserRepository
from app.core.command import BaseCommand, BaseCommandHandler
from app.core.depends import MailService
from app.core.services.mail.service import EmailData


@dataclass(frozen=True)
class SendVerifyCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class SendVerifyCommandHandler(BaseCommandHandler[SendVerifyCommand, None]):
    session: AsyncSession
    user_repository: UserRepository
    mail_service: MailService

    async def handle(self, command: SendVerifyCommand) -> None:
        user = await self.user_repository.get_by_email(self.session, email=command.email)
        if not user:
            return

        token = generate_verify_token(email=command.email)
        email_data = EmailData(subject="Код для верификации почты", recipient=user.email)
        template = VerifyTokenTemplate(
            username=user.username,
            link=f'{app_config.app_url}/verify_email?token={token}',
            token=token,
            valid_minutes=auth_config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES,
        )

        await self.mail_service.queue(template=template, email_data=email_data)