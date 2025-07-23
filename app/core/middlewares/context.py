from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog


class ContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request.state.request_id = uuid4()
        with structlog.contextvars.bound_contextvars(request_id=str(request.state.request_id)):
            return await call_next(request)