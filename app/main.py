from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from starlette.middleware.cors import CORSMiddleware

from app.auth.routers import router_v1 as auth_router_v1
from app.core.configs.app import app_config
from app.core.middlewares import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(app_config.redis_url)
    await FastAPILimiter.init(redis_client)
    yield
    await redis_client.aclose()


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(LoggingMiddleware)

    if app_config.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin).strip('/') for origin in app_config.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )


def setup_router(app: FastAPI) -> None:
    app.include_router(auth_router_v1, prefix=app_config.API_V1_STR)


def init_app() -> FastAPI:

    app = FastAPI(
        openapi_url=f'{app_config.API_V1_STR}/openapi.json' if app_config.ENVIRONMENT in ['local', 'staging'] else None,
        lifespan=lifespan,
    )

    setup_middleware(app)
    setup_router(app)

    return app

