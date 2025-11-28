from datetime import timedelta
import pytest
import pytest_asyncio
from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import auth_config
from app.auth.models.user import User
from app.auth.repositories.oauth import OAuthCodeRepository
from app.auth.repositories.permission import PermissionInvalidateRepository, PermissionRepository
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.repositories.session import SessionRepository, TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.hash import HashService
from app.auth.services.jwt import JWTManager
from app.auth.services.session import SessionManager
from tests.integration.auth.factories import UserFactory


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
async def session_repository(db_session: AsyncSession) -> SessionRepository:
    return SessionRepository(db_session)

@pytest.fixture
def token_blacklist_repository(redis_client: Redis) -> TokenBlacklistRepository:
    return TokenBlacklistRepository(
        client=redis_client
    )

@pytest.fixture
def role_blacklist(redis_client: Redis) -> RoleInvalidateRepository:
    return RoleInvalidateRepository(
        client=redis_client
    )

@pytest.fixture
def permission_blacklist(redis_client: Redis) -> PermissionInvalidateRepository:
    return PermissionInvalidateRepository(
        client=redis_client
    )

@pytest.fixture
def oauth_code_repository(redis_client: Redis) -> OAuthCodeRepository:
    return OAuthCodeRepository(
        client=redis_client
    )


@pytest.fixture
def hash_service() -> HashService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return HashService(pwd_context=pwd_context)


@pytest.fixture
def jwt_manager(token_blacklist_repository: TokenBlacklistRepository) -> JWTManager:
    return JWTManager(
        jwt_secret=auth_config.JWT_SECRET_KEY,
        jwt_algorithm=auth_config.JWT_ALGORITHM,
        access_token_expire_minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS,
        token_blacklist=token_blacklist_repository
    )


@pytest.fixture
def session_manager(session_repository: SessionRepository) -> SessionManager:
    return SessionManager(session_repository)


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
        user_jwt_data = UserJWTData.create_from_user(user, device_id=device_id or "Chrome/100.0")
        token_group = jwt_manager.create_token_pair(user_jwt_data)
        return token_group.access_token

    return _create

@pytest.fixture
def auth_headers(create_access_token):
    def _headers(user: User) -> dict[str, str]:
        token = create_access_token(user)
        return {"Authorization": f"Bearer {token}"}

    return _headers