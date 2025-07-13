from dataclasses import dataclass

from app.auth.emails.templates import VerifyTokenTemplate
from app.auth.security import generate_verify_token
from app.core.events.event import BaseEvent, BaseEventHandler
from app.core.services.mail.service import EmailData, MailServiceInterface


@dataclass(frozen=True)
class CreatedUserEvent(BaseEvent):
    user_id: int
    email: str

    __event_name__: str = "user_created"


@dataclass(frozen=True)
class SendVerifyEventHandler(BaseEventHandler[CreatedUserEvent, None]):
    mail_service: MailServiceInterface

    async def handle(self, event: CreatedUserEvent) -> None:
        email_data = EmailData(subject='Successful registration', recipient=event.email)
        verify_token = generate_verify_token(email=event.email)
        template = VerifyTokenTemplate(
            email=event.email,
            token=verify_token,
        )
        await self.mail_service.queue(template=template, email_data=email_data)