from aiocache import caches, BaseCache

from app.core.configs.app import app_config


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