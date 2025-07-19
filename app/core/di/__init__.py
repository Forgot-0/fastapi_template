from app.core.di.cache import CacheProvider
from app.core.di.db import DBProvider
from app.core.di.services import ServicesProvider
from app.core.di.repositories import RepositoriesProvider
from app.core.di.handlers import HandlersProvider
from app.core.di.events import EventsProvider
from app.core.di.mediator import MediatorProvider


def get_core_providers():
    return [
        DBProvider(),
        CacheProvider(),
        ServicesProvider(),
        RepositoriesProvider(),
        HandlersProvider(),
        EventsProvider(),
        MediatorProvider(),
    ]