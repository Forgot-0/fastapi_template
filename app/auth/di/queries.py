from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.queries.auth.get_by_token import GetByAcccessTokenQueryHandler
from app.auth.repositories.user import UserRepository


class AuthQueryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_by_access_token_query_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> GetByAcccessTokenQueryHandler:
        return GetByAcccessTokenQueryHandler(
            session=session,
            user_repository=user_repository,
        )
