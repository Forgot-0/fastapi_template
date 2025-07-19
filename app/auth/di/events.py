from dishka import Provider, Scope, provide

from app.auth.events.users.created import SendVerifyEventHandler
from app.core.services.mail.service import MailServiceInterface
from app.core.services.queue.service import QueueServiceInterface


class AuthEventProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def send_verify_event_handler(
        self,
        mail_service: MailServiceInterface,
    ) -> SendVerifyEventHandler:
        return SendVerifyEventHandler(
            mail_service=mail_service,
        )
