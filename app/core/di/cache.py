from aiocache import caches, BaseCache
from dishka import Provider, Scope, provide

from app.core.configs.app import app_config
from app.core.services.cache.aiocache.service import AioCacheService
from app.core.services.cache.base import CacheServiceInterface




class CacheProvider(Provider):
    scope = Scope.APP

    @provide
    async def inti_aiocache(self) -> BaseCache:
        caches.set_config(
            {
                'default': {
                    'cache': 'aiocache.RedisCache',
                    'endpoint': app_config.REDIS_HOST,
                    'port': app_config.REDIS_PORT,
                    'timeout': 1,
                    'serializer': {'class': 'aiocache.serializers.PickleSerializer'},
                }
            }
        )
        cache_provider: BaseCache = caches.get('default') # type: ignore
        return cache_provider

    @provide
    async def cache_service(self, cache_provider: BaseCache) -> CacheServiceInterface:
        return AioCacheService(cache_provider)