from dishka import Provider, Scope, provide

from app.core.configs.app import app_config
from app.core.configs.smtp import SMTPConfig
from app.core.services.mail.aiosmtplib.service import AioSmtpLibMailService
from app.core.services.mail.service import BaseMailService
from app.core.services.queues.service import QueueServiceInterface


class MailProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_smtp_config(self) -> SMTPConfig:
        return SMTPConfig(
            hostname=app_config.SMTP_HOST,
            port=app_config.SMTP_PORT,
            username=app_config.SMTP_USER,
            password=app_config.SMTP_PASSWORD,
            use_tls=app_config.SMTP_TLS
        )

    @provide
    async def get_mail_service(
        self,
        queue_service: QueueServiceInterface,
        smtp_config: SMTPConfig
    ) -> BaseMailService:
        return AioSmtpLibMailService(queue_service, smtp_config=smtp_config)
