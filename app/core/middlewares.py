import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.depends import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        logger.info(
            'request',
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            processing_time=time.time() - start_time,
        )

        return response 