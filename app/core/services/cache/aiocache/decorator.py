from dataclasses import dataclass
import hashlib
import json
from collections.abc import Callable
from functools import wraps

from aiocache import BaseCache


@dataclass
class AioCachedDecorator:
    cache: BaseCache

    def __call__(self, ttl: int, key_builder: Callable | None = None) -> Callable:
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = (
                    key_builder(func, *args, **kwargs) if key_builder else self._build_key(func, *args, **kwargs)
                )

                cached_value = await self.cache.get(cache_key)
                if cached_value is not None:
                    return cached_value

                result = await func(*args, **kwargs)
                await self.cache.set(key=cache_key, value=result, ttl=ttl)
                return result

            return wrapper

        return decorator

    def _build_key(self, func: Callable, *args, **kwargs) -> str:
        key_data = {'func': func.__name__, 'args': args, 'kwargs': kwargs}

        json_str = json.dumps(key_data, sort_keys=True)
        hash_str = hashlib.md5(json_str.encode()).hexdigest()

        return f'{func.__name__}:{hash_str}'