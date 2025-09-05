from contextlib import asynccontextmanager
import logging

from dishka.integrations.faststream import FastStreamProvider, setup_dishka
from faststream import ContextRepo, FastStream
from faststream.kafka import KafkaBroker


from app.core.configs.app import app_config
from app.core.di.container import create_container
from app.core.log.init import configure_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(context: ContextRepo):
    logger.info("Starting FastStream")
    yield
    logger.info("Shutting down FastStream")


def setup_router(broker: KafkaBroker) -> None:
    ...


def init_consumers() -> FastStream:
    broker = KafkaBroker(app_config.BROKER_URL)

    app = FastStream(
        broker
    )

    configure_logging()
    container = create_container(FastStreamProvider())
    setup_dishka(container=container, app=app, auto_inject=True)
    setup_router(broker)
    return app