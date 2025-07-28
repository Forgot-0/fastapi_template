from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider
from dishka.integrations.taskiq import TaskiqProvider

from app.auth.di import get_auth_providers
from app.core.di import get_core_providers


def create_container() -> AsyncContainer:
    """Create and configure the main DI container with all providers."""
    providers = [
        # Core providers
        *get_core_providers(),

        # Module providers
        *get_auth_providers(),
    ]

    return make_async_container(*providers, FastapiProvider(), TaskiqProvider())
