from app.auth.di.repositories import AuthRepositoryProvider
from app.auth.di.queries import AuthQueryProvider
from app.auth.di.events import AuthEventProvider
from app.auth.di.commands import AuthCommandProvider
from app.auth.di.services import AuthServiceProvider


def get_auth_providers():
    return [
        AuthRepositoryProvider(),
        AuthServiceProvider(),
        AuthCommandProvider(),
        AuthQueryProvider(),
        AuthEventProvider(),
    ]