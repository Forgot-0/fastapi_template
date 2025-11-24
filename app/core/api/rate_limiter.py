from fastapi import Request
from fastapi_limiter.depends import RateLimiter
from starlette.responses import Response


class ConfigurableRateLimiter(RateLimiter):
    # Можно сделать глабальные настройки для проекта, но пока тут их нет(
    async def __call__(self, request: Request, response: Response) -> None:
        await super().__call__(request=request, response=response)
