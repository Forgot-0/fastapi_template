from taskiq import AsyncBroker, InMemoryBroker
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend
from app.core.configs.app import app_config
from app.core.di.tasks import regester_core_task


broker: AsyncBroker

if app_config.ENVIRONMENT == 'testing':
    broker = InMemoryBroker()
else:
    broker = ListQueueBroker(url=app_config.QUEUE_REDIS_BROKER_URL)
    broker.with_result_backend(RedisAsyncResultBackend(app_config.QUEUE_REDIS_RESULT_BACKEND))

regester_core_task(broker)