from taskiq import AsyncBroker

from app.core.services.mail.aiosmtplib.task import SendEmail


def register_tasks(broker: AsyncBroker) -> None:

    broker.register_task(
        SendEmail.run,
        task_name=SendEmail.get_name()
    )
