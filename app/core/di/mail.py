from dishka import Provider, Scope, provide


from app.core.configs.app import app_config
from app.core.services.mail.aiosmtplib.service import AioSmtpLibMailService
from app.core.services.mail.service import MailServiceInterface
from app.core.services.queue.service import QueueServiceInterface


class MailProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_mail_service(self, queue_service: QueueServiceInterface) -> MailServiceInterface:
        return AioSmtpLibMailService(queue_service)
