from fastapi import Request
from fastapi_limiter.depends import RateLimiter
from starlette.responses import Response

from app.core.configs.app import app_config


class ConfigurableRateLimiter(RateLimiter):
    # Можно сделать глабальные настройки для проекта, но пока тут их нет(
    async def __call__(self, request: Request, response: Response):
        await super().__call__(request=request, response=response)


    @classmethod
    async def get_identifier_with_params(cls, request: Request):
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0]
        else:
            ip = request.client.host # type: ignore
        return ":".join((ip, request.scope["path"], f"{request.query_params.values()}", f"{await request.json()}"))

    @classmethod
    async def get_identifier_by_body(cls, request: Request):
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0]
        else:
            ip = request.client.host # type: ignore
        body = await request.json()
        return ":".join((ip, request.scope["path"], f"{body}"))
