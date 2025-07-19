from dishka import Provider, Scope, provide

from app.auth.events.users.created import CreatedUserEventHandler
from app.auth.events.users.verified import VerifiedUserEventHandler
from app.auth.events.users.password_reset import PasswordResetEventHandler
from app.core.services.mail.service import MailServiceInterface
from app.core.services.queue.service import QueueServiceInterface


class AuthEventProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def created_user_event_handler(
        self,
        mail_service: MailServiceInterface,
        queue_service: QueueServiceInterface,
    ) -> CreatedUserEventHandler:
        return CreatedUserEventHandler(
            mail_service=mail_service,
            queue_service=queue_service,
        )

    @provide
    def verified_user_event_handler(
        self,
        mail_service: MailServiceInterface,
        queue_service: QueueServiceInterface,
    ) -> VerifiedUserEventHandler:
        return VerifiedUserEventHandler(
            mail_service=mail_service,
            queue_service=queue_service,
        )

    @provide
    def password_reset_event_handler(
        self,
        mail_service: MailServiceInterface,
        queue_service: QueueServiceInterface,
    ) -> PasswordResetEventHandler:
        return PasswordResetEventHandler(
            mail_service=mail_service,
            queue_service=queue_service,
        )