from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from starlette.middleware.cors import CORSMiddleware

from app.auth.routers import router_v1 as auth_router_v1
from app.core.configs.app import app_config
from app.core.middlewares import LoggingMiddleware
from app.core.di import setup_di
from app.core.di.initialize import startup_di_system, shutdown_di_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DI system with all handler registrations
    await startup_di_system()
    
    # Redis setup for rate limiting
    redis_client = redis.from_url(app_config.redis_url)
    await FastAPILimiter.init(redis_client)
    
    yield
    
    # Cleanup
    await shutdown_di_system()
    await redis_client.aclose()


def setup_middleware(app: FastAPI) -> None:
    """Configure application middleware."""
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
    """Configure application routers."""
    app.include_router(auth_router_v1, prefix=app_config.API_V1_STR)


def init_app() -> FastAPI:
    """Initialize and configure the FastAPI application."""
    app = FastAPI(
        title=app_config.PROJECT_NAME,
        version="1.0.0",
        description="A modular FastAPI application with comprehensive DI using Dishka",
        openapi_url=f'{app_config.API_V1_STR}/openapi.json' if app_config.ENVIRONMENT in ['local', 'staging'] else None,
        lifespan=lifespan,
    )

    # Setup dependency injection
    setup_di(app)
    
    # Setup middleware and routing
    setup_middleware(app)
    setup_router(app)

    return app


# Create the app instance
app = init_app()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": app_config.ENVIRONMENT,
        "project": app_config.PROJECT_NAME
    }


# DI system info endpoint (for development/debugging)
@app.get("/di-info")
async def di_info():
    """Get information about registered DI handlers (development only)."""
    if app_config.ENVIRONMENT not in ['local', 'development']:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    
    from app.core.di.initialize import get_registered_handlers_info
    return get_registered_handlers_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=app_config.HOST,
        port=app_config.PORT,
        reload=app_config.ENVIRONMENT == "local",
    )

