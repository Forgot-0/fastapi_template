from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.configs.app import app_config
from app.auth.config import auth_config
from app.auth.emails.templates import ResetTokenTemplate
from app.auth.repositories.user import UserRepository
from app.auth.security import generate_reset_token
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.services.mail.service import EmailData, MailServiceInterface


@dataclass(frozen=True)
class SendResetPasswordCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class SendResetPasswordCommandHandler(BaseCommandHandler[SendResetPasswordCommand, None]):
    session: AsyncSession
    user_repository: UserRepository
    mail_service: MailServiceInterface

    async def handle(self, command: SendResetPasswordCommand) -> None:
        user = await self.user_repository.get_by_email(self.session, email=command.email)
        if not user:
            return

        token = generate_reset_token(email=command.email)
        email_data = EmailData(subject="Код для сброса пароля", recipient=user.email)
        template = ResetTokenTemplate(
            username=user.username,
            link=f'{app_config.app_url}/reset_password?token={token}',
            token=token,
            valid_minutes=auth_config.EMAIL_RESET_TOKEN_EXPIRE_MINUTES,
        )

        await self.mail_service.queue(template=template, email_data=email_data)