from typing import Any

from app.core.services.cache.base import CacheServiceInterface
from app.core.services.cache.aiocache.decorator import AioCachedDecorator
from app.core.services.cache.aiocache.service import AioCacheService
from app.core.services.cache.aiocache.init import cache_provider


def get_cache_service() -> CacheServiceInterface:
    return AioCacheService(cache_provider)


def get_cached_decorator() -> Any:
    return AioCachedDecorator(cache_provider)