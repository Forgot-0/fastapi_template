from dataclasses import dataclass

from app.auth.emails.templates import VerifyTokenTemplate
from app.auth.exceptions import WrongDataException
from app.auth.models.user import CreatedUserEvent
from app.auth.repositories.user import UserRepository
from app.core.events.event import BaseEventHandler
from app.core.services.mail.service import BaseMailService, EmailData



@dataclass(frozen=True)
class SendVerifyEventHandler(BaseEventHandler[CreatedUserEvent, None]):
    user_repository: UserRepository
    mail_service: BaseMailService

    async def __call__(self, event: CreatedUserEvent) -> None:
        user = await self.user_repository.get_by_email(email=event.email)

        if not user:
            raise WrongDataException()

        # token = generate_verify_token(email=event.email)
        # email_data = EmailData(subject="Код для верификации почты", recipient=user.email)
        # template = VerifyTokenTemplate(
        #     email=user.email,
        #     token=token,
        # )
        # await self.mail_service.queue(template=template, email_data=email_data)
        ...