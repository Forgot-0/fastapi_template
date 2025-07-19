from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.queries.users.get_by_id import GetUserByIdQueryHandler
from app.auth.queries.users.get_by_email import GetUserByEmailQueryHandler
from app.auth.queries.users.get_list import GetUserListQueryHandler
from app.auth.queries.auth.get_current_user import GetCurrentUserQueryHandler
from app.auth.repositories.user import UserRepository
from app.auth.repositories.token import TokenRepository


class AuthQueryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_by_id_query_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> GetUserByIdQueryHandler:
        return GetUserByIdQueryHandler(
            session=session,
            user_repository=user_repository,
        )

    @provide
    def get_user_by_email_query_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> GetUserByEmailQueryHandler:
        return GetUserByEmailQueryHandler(
            session=session,
            user_repository=user_repository,
        )

    @provide
    def get_user_list_query_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> GetUserListQueryHandler:
        return GetUserListQueryHandler(
            session=session,
            user_repository=user_repository,
        )

    @provide
    def get_current_user_query_handler(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        token_repository: TokenRepository,
    ) -> GetCurrentUserQueryHandler:
        return GetCurrentUserQueryHandler(
            session=session,
            user_repository=user_repository,
            token_repository=token_repository,
        )