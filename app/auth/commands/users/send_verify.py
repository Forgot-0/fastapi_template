from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.emails.templates import VerifyTokenTemplate
from app.auth.exceptions import WrongDataException
from app.auth.repositories.user import UserRepository
from app.core.commands import BaseCommand, BaseCommandHandler
from app.core.services.mail.service import BaseMailService, EmailData


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class SendVerifyCommand(BaseCommand):
    email: str


@dataclass(frozen=True)
class SendVerifyCommandHandler(BaseCommandHandler[SendVerifyCommand, None]):
    session: AsyncSession
    user_repository: UserRepository
    mail_service: BaseMailService

    async def handle(self, command: SendVerifyCommand) -> None:
        # user = await self.user_repository.get_by_email(email=command.email)

        # if not user:
        #     raise WrongDataException()

        # token = generate_verify_token(email=command.email)
        # email_data = EmailData(subject="Код для верификации почты", recipient=user.email)
        # template = VerifyTokenTemplate(
        #     email=user.email,
        #     token=token,
        # )
        # await self.mail_service.queue(template=template, email_data=email_data)
        # logger.info("Send verify email", extra={"email": user.email})
        ...