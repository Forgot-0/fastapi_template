from app.core.di.cache import CacheProvider
from app.core.di.db import DBProvider
from app.core.di.config import ConfigProvider
from app.core.di.services import ServiceProvider
from app.core.di.mediator import MediatorProvider
from app.core.di.events import EventProvider
from app.core.di.container import create_container, container
from app.core.di.fastapi import setup_di, inject, di_depends, get_container


def get_core_providers():
    return [
        ConfigProvider(),
        DBProvider(),
        CacheProvider(),
        ServiceProvider(),
        MediatorProvider(),
        EventProvider(),
    ]


__all__ = [
    'CacheProvider',
    'DBProvider', 
    'ConfigProvider',
    'ServiceProvider',
    'MediatorProvider',
    'EventProvider',
    'get_core_providers',
    'create_container',
    'container',
    'setup_di',
    'inject',
    'di_depends',
    'get_container',
]