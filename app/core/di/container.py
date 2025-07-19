from dishka import AsyncContainer, make_async_container

from app.auth.di import get_auth_providers
from app.core.di.cache import CacheProvider
from app.core.di.db import DBProvider
from app.core.di.events import EventProvider
from app.core.di.mail import MailProvider
from app.core.di.mediator import MediatorProvider
from app.core.di.queue import QueueProvider


def create_container() -> AsyncContainer:
    """Create and configure the main DI container with all providers."""
    providers = [
        # Core providers
        DBProvider(),
        CacheProvider(),
        MediatorProvider(),
        EventProvider(),
        QueueProvider(),
        MailProvider(),
        
        # Module providers
        *get_auth_providers(),
    ]

    return make_async_container(*providers)
