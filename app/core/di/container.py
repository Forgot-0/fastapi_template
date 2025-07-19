from dishka import Container, make_container

from app.core.di.config import ConfigProvider
from app.core.di.db import DBProvider
from app.core.di.cache import CacheProvider
from app.core.di.services import ServiceProvider
from app.core.di.mediator import MediatorProvider
from app.core.di.events import EventProvider
from app.core.di.tasks import TaskProvider
from app.auth.di import get_auth_providers


def create_container() -> Container:
    """Create and configure the main DI container with all providers."""
    providers = [
        # Core providers
        ConfigProvider(),
        DBProvider(),
        CacheProvider(),
        ServiceProvider(),
        MediatorProvider(),
        EventProvider(),
        TaskProvider(),
        
        # Module providers
        *get_auth_providers(),
    ]
    
    return make_container(*providers)


# Global container instance
container = create_container()