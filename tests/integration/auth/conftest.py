from datetime import timedelta
import pytest
import pytest_asyncio
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from app.auth.repositories.permission import PermissionRepository
from app.auth.repositories.role import RoleRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.hash import HashService
from app.auth.services.jwt import JWTManager
from app.core.utils import fromtimestamp, now_utc
from tests.integration.auth.factories import UserFactory



@pytest.fixture
def hash_service() -> HashService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return HashService(pwd_context=pwd_context)


@pytest.fixture
def jwt_manager() -> JWTManager:

    class MockTokenBlacklist:
        def __init__(self):
            self.tokens = {}
            self.users = {}

        async def add_jwt_token(self, jti: str, expiration: timedelta):
            self.tokens[jti] = now_utc().timestamp()

        async def get_token_backlist(self, jti: str):
            return fromtimestamp(self.tokens.get(jti, 0.00))

        async def get_user_backlist(self, user_id: int):
            return fromtimestamp(self.users.get(user_id, 0.00))

    return JWTManager(
        jwt_secret="test_secret_key_for_testing_only",
        jwt_algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
        token_blacklist=MockTokenBlacklist(),  # type: ignore
    )

@pytest_asyncio.fixture
async def user_repository(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session)


@pytest_asyncio.fixture
async def role_repository(db_session: AsyncSession) -> RoleRepository:
    return RoleRepository(session=db_session)


@pytest_asyncio.fixture
async def permission_repository(db_session: AsyncSession) -> PermissionRepository:
    return PermissionRepository(session=db_session)


@pytest_asyncio.fixture
async def standard_user(
    db_session: AsyncSession,
    user_repository: UserRepository,
    hash_service: HashService,
    role_repository: RoleRepository,
) -> User:
    role = await role_repository.get_with_permission_by_name("user")
    if role is None:
        raise
    user = UserFactory.create_verified(
        email="standard@example.com",
        username="standarduser",
        password_hash=hash_service.hash_password("TestPass123!"),
        roles={role, },
    )

    await user_repository.create(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def admin_user(
    db_session: AsyncSession,
    user_repository: UserRepository,
    hash_service: HashService,
    role_repository: RoleRepository,
) -> User:
    role = await role_repository.get_with_permission_by_name("super_admin")
    if role is None:
        raise
    user = UserFactory.create_verified(
        email="admin@example.com",
        username="adminuser",
        password_hash=hash_service.hash_password("AdminPass123!"),
        roles={role, },
    )

    await user_repository.create(user)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
async def unverified_user(
    db_session: AsyncSession,
    user_repository: UserRepository,
    hash_service: HashService,
    role_repository: RoleRepository,
) -> User:
    role = await role_repository.get_with_permission_by_name("user")
    if role is None:
        raise
    user = UserFactory.create(
        email="unverified@example.com",
        username="unverifieduser",
        password_hash=hash_service.hash_password("TestPass123!"),
        is_verified=False,
        roles={role, },
    )

    await user_repository.create(user)
    await db_session.commit()

    return user

@pytest.fixture
def create_access_token(jwt_manager: JWTManager):

    def _create(user: User, device_id: str | None = None) -> str:
        user_jwt_data = UserJWTData.create_from_user(user, device_id=device_id)
        token_group = jwt_manager.create_token_pair(user_jwt_data)
        return token_group.access_token

    return _create

@pytest.fixture
def auth_headers(create_access_token):
    def _headers(user: User) -> dict[str, str]:
        token = create_access_token(user)
        return {"Authorization": f"Bearer {token}"}

    return _headers