from app.core.di.cache import CacheProvider
from app.core.di.db import DBProvider


def get_core_providers():
    return [
        DBProvider(),
        CacheProvider(),
    ]