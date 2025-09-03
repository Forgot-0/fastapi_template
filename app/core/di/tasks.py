from taskiq import AsyncBroker

from app.auth.tasks import RemoveInactiveTokens
from app.core.services.mail.aiosmtplib.task import SendEmail


def regester_core_task(broker: AsyncBroker) -> None:
    broker.register_task(
        SendEmail.run, task_name=SendEmail.get_name()
    )

    broker.register_task(
        RemoveInactiveTokens.run,
        task_name=RemoveInactiveTokens.get_name(),
        schedule=[{"cron": "0 0 * * *"}],
    )
    broker.register_task(
        SendEmail.run,
        task_name=SendEmail.get_name()
    )