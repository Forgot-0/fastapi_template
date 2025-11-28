import pytest
from passlib.context import CryptContext
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.oauth import OAuthCodeRepository
from app.auth.repositories.permission import PermissionInvalidateRepository, PermissionRepository
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.repositories.session import SessionRepository, TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.hash import HashService
from app.auth.services.jwt import JWTManager
from app.auth.services.rbac import RBACManager
from app.auth.services.session import SessionManager



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
        jwt_secret="test_secret_key_for_testing_only",
        jwt_algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
        token_blacklist=token_blacklist_repository
    )

@pytest.fixture
def rbac_manager() -> RBACManager:
    return RBACManager()

@pytest.fixture
def session_manager(session_repository: SessionRepository) -> SessionManager:
    return SessionManager(session_repository)


@pytest.fixture
def regular_user_jwt() -> UserJWTData:
    return UserJWTData(
        id="1",
        roles=["user"],
        permissions=["user:view"],
        security_level=1,
        device_id="device_1"
    )

@pytest.fixture
def admin_user_jwt() -> UserJWTData:
    return UserJWTData(
        id="2",
        roles=["super_admin"],
        permissions=["user:create", "user:delete", "role:create"],
        security_level=10,
        device_id="device_2"
    )