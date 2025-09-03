from dishka.integrations.taskiq import TaskiqProvider, setup_dishka
from taskiq import AsyncBroker, InMemoryBroker, TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend, RedisScheduleSource

from app.core.configs.app import app_config
from app.core.di.container import create_container
from app.core.di.tasks import regester_core_task
from app.core.message_brokers.base import BaseMessageBroker


container = create_container(TaskiqProvider())

def init_broker() -> AsyncBroker:

    broker: AsyncBroker

    if app_config.ENVIRONMENT == 'testing':
        broker = InMemoryBroker()
    else:
        broker = ListQueueBroker(url=app_config.QUEUE_REDIS_BROKER_URL)
        broker.with_result_backend(RedisAsyncResultBackend(app_config.QUEUE_REDIS_RESULT_BACKEND))

    setup_dishka(container=container, broker=broker)
    regester_core_task(broker)
    return broker


broker = init_broker()


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    message_broker = await container.get(BaseMessageBroker)
    await message_broker.start()


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    message_broker = await container.get(BaseMessageBroker)
    await message_broker.close()




redis_schedule_source = RedisScheduleSource(
        url=app_config.QUEUE_REDIS_BROKER_URL,
    )

scheduler_taksiq = TaskiqScheduler(
    broker=broker,
    sources=[redis_schedule_source, LabelScheduleSource(broker=broker)],
)