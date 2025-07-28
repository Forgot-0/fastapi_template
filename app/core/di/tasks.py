from taskiq import AsyncBroker

from app.core.services.mail.aiosmtplib.task import SendEmail


def regester_core_task(broker: AsyncBroker) -> None:
    broker.register_task(
        SendEmail.run, task_name=SendEmail.get_name()
    )