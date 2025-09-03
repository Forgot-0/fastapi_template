from contextlib import asynccontextmanager
import logging

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, HTTPException, Request
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from starlette.middleware.cors import CORSMiddleware

from app.auth.routers import router_v1 as auth_router_v1
from app.core.configs.app import app_config
from app.core.di.container import create_container
from app.core.exceptions import ApplicationException
from app.core.log.init import configure_logging
from app.core.message_brokers.base import BaseMessageBroker
from app.core.middlewares.context import ContextMiddleware
from app.core.middlewares.logging import LoggingMiddleware


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(app_config.redis_url)
    await FastAPILimiter.init(redis_client)
    message_broker = await app.state.dishka_container.get(BaseMessageBroker)
    await message_broker.start()
    yield
    await redis_client.aclose()
    await message_broker.close()
    await app.state.dishka_container.close()


def handle_application_exeption(request: Request, exception: ApplicationException):
    logger.exception(
        "Application exception",
        exc_info=exception,
        extra={"status": exception.status, "detail": exception.message}
    )
    raise HTTPException(
        detail={"error": exception.message},
        status_code=exception.status
    )

def setup_middleware(app: FastAPI, container: AsyncContainer) -> None:
    app.add_middleware(LoggingMiddleware)

    if app_config.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin).strip('/') for origin in app_config.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
    app.add_middleware(ContextMiddleware)


def setup_router(app: FastAPI) -> None:
    app.include_router(auth_router_v1, prefix=app_config.API_V1_STR)


def init_app() -> FastAPI:

    app = FastAPI(
        openapi_url=f'{app_config.API_V1_STR}/openapi.json' if app_config.ENVIRONMENT in ['local', 'staging'] else None,
        lifespan=lifespan,
    )

    configure_logging()
    container = create_container()
    setup_dishka(container=container, app=app)

    setup_middleware(app, container)
    setup_router(app)

    app.add_exception_handler(ApplicationException, handle_application_exeption) # type: ignore

    return app

