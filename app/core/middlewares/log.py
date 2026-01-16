import logging
import time

from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                processing_time = time.time() - start_time
                logger.info("request", extra={
                    "method": scope["method"],
                    "path": scope["path"],
                    "status_code": message["status"],
                    "processing_time": processing_time
                })
            await send(message)

        await self.app(scope, receive, send_wrapper)
