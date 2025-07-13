from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import generate_verify_token
from app.auth.emails.templates import VerifyTokenTemplate
from app.auth.repositories.user import UserRepository
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.services.mail.service import EmailData, MailServiceInterface


@dataclass(frozen=True)
class SendVerifyCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class SendVerifyCommandHandler(BaseCommandHandler[SendVerifyCommand, None]):
    session: AsyncSession
    user_repository: UserRepository
    mail_service: MailServiceInterface

    async def handle(self, command: SendVerifyCommand) -> None:
        user = await self.user_repository.get_by_email(self.session, email=command.email)
        if not user:
            return

        token = generate_verify_token(email=command.email)
        email_data = EmailData(subject="Код для верификации почты", recipient=user.email)
        template = VerifyTokenTemplate(
            email=user.email,
            token=token,
        )

        await self.mail_service.queue(template=template, email_data=email_data)