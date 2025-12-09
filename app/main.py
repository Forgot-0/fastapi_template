import logging
from contextlib import asynccontextmanager
from typing import Any

from prometheus_fastapi_instrumentator.instrumentation import PrometheusFastApiInstrumentator
import redis.asyncio as redis
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi_limiter import FastAPILimiter
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.routers import router_v1 as auth_router_v1
from app.core.routers import router as core_router
from app.core.api.builder import create_response
from app.core.api.schemas import ErrorDetail, ErrorResponse, ORJSONResponse
from app.core.configs.app import app_config
from app.core.di.container import create_container
from app.core.exceptions import ApplicationException, ValidationException
from app.core.log.init import configure_logging
from app.core.message_brokers.base import BaseMessageBroker
from app.core.middlewares.context import ContextMiddleware
from app.core.middlewares.log import LoggingMiddleware
from app.core.utils import now_utc
from app.init_data import init_data
from app.pre_start import pre_start


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) :
    logger.info("Starting FastAPI")
    async with app.state.dishka_container() as request_container:
        session = await request_container.get(AsyncSession)
        await pre_start(session)
        await init_data(session)

    redis_client = redis.from_url(app_config.redis_url)
    await FastAPILimiter.init(redis_client)
    message_broker: BaseMessageBroker = await app.state.dishka_container.get(BaseMessageBroker)
    await message_broker.start()
    yield
    await redis_client.aclose()
    await message_broker.close()
    await app.state.dishka_container.close()
    logger.info("Shutting down FastAPI")


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(LoggingMiddleware)

    if app_config.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin).strip("/") for origin in app_config.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.add_middleware(ContextMiddleware)


def setup_router(app: FastAPI) -> None:
    app.include_router(core_router)
    app.include_router(auth_router_v1, prefix=app_config.API_V1_STR)


def handle_application_exeption(request: Request, exc: ApplicationException) -> ORJSONResponse:
    logger.error(
        "Application exception",
        exc_info=exc,
        extra={"status": exc.status, "title": exc.message, "detail": exc.detail, "code": exc.code}
    )
    return ORJSONResponse(
        status_code=exc.status,
        content=ErrorResponse(
            error=ErrorDetail(
                code=exc.code,
                message=exc.message,
                detail=exc.detail
            ),
            status=exc.status,
            request_id=request.state.request_id.hex,
            timestamp=now_utc().timestamp()
        ),
    )

def handle_validation_exeption(request: Request, exc: RequestValidationError) -> ORJSONResponse:
    logger.error(
        "Validation exception",
        exc_info=exc,
        extra={"error": exc.errors()}
    )
    return ORJSONResponse(
        status_code=422,
        content=ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION",
                message="Validation exception",
                detail=jsonable_encoder(exc.errors()),
            ),
            status=422,
            request_id=request.state.request_id.hex,
            timestamp=now_utc().timestamp()
        ),
    )

def handle_uncown_exception(request: Request, exc: Exception) -> ORJSONResponse:
    logger.error(
        "Uncown exception",
        exc_info=exc,
        extra={"error": exc}
    )
    return ORJSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code="UNCOWN_EXCEPTION",
                message="Uncown exception",
            ),
            status=500,
            request_id=request.state.request_id.hex,
            timestamp=now_utc().timestamp()
        ),
    )

def custom_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    response_def = create_response(ValidationException(), description="Validation error")

    components = openapi_schema.setdefault("components", {})
    responses = components.setdefault("responses", {})

    responses["HTTPValidationError"] = {
        "description": response_def.get("description", "Validation Error"),
        "content": response_def.get("content", {"application/json": {"example": {}}}),
    }

    model = response_def.get("model")
    if model is not None:

        model_schema = model.model_json_schema(ref_template="#/components/schemas/{model}")
        components_schemas = components.setdefault("schemas", {})
        model_name = getattr(model, "__name__", None) or model.__class__.__name__
        if isinstance(model_schema, dict):
            defs = (
                model_schema.get("$defs") or
                model_schema.get("definitions") or model_schema.get("components", {}).get("schemas")
            )
            if defs and isinstance(defs, dict):
                for k, v in defs.items():
                    components_schemas.setdefault(k, v)
            if "$ref" not in model_schema:
                components_schemas.setdefault(model_name, model_schema)
                schema_ref = {"$ref": f"#/components/schemas/{model_name}"}
            else:
                schema_ref = model_schema
            content = responses["HTTPValidationError"].setdefault("content", {})
            app_json = content.setdefault("application/json", {})
            app_json["schema"] = schema_ref

    for path, path_item in openapi_schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue
            responses_obj = operation.get("responses", {})
            if "422" in responses_obj:
                responses_obj["422"] = {"$ref": "#/components/responses/HTTPValidationError"}

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def init_app() -> FastAPI:

    app = FastAPI(
        openapi_url=(
            f"{app_config.API_V1_STR}/openapi.json"
            if app_config.ENVIRONMENT in ["local", "testing"]
            else None
        ),
        lifespan=lifespan,
    )

    PrometheusFastApiInstrumentator().instrument(
        app,
        latency_lowr_buckets=(0.1, 0.5, 1, 1.5, 2, 2.5, 3)
    ).expose(app, should_gzip=True, tags=["core"])

    configure_logging()
    container = create_container()
    setup_dishka(container=container, app=app)

    setup_middleware(app)
    setup_router(app)

    app.add_exception_handler(Exception, handle_uncown_exception)
    app.add_exception_handler(ApplicationException, handle_application_exeption) # type: ignore
    app.add_exception_handler(RequestValidationError, handle_validation_exeption) # type: ignore
    app.openapi = lambda: custom_openapi(app)
    return app

