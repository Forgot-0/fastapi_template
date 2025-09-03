from dishka import Provider, Scope, provide

from app.auth.queries.auth.get_by_token import GetByAccessTokenQueryHandler


class AuthQueryProvider(Provider):
    scope = Scope.REQUEST

    get_user_by_access_token_query_handler = provide(GetByAccessTokenQueryHandler)
