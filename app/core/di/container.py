from dishka import AsyncContainer, make_async_container

from app.auth.providers import AuthModuleProvider
from app.core.di import get_core_providers


def create_container(*app_providers) -> AsyncContainer:
    """Create and configure the main DI container with all providers."""
    providers = [
        # Core providers
        *get_core_providers(),

        # Module providers
        AuthModuleProvider(),
    ]

    return make_async_container(*providers, *app_providers)
