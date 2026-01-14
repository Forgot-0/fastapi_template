import pytest
from passlib.context import CryptContext
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import auth_config
from app.auth.repositories.oauth import OAuthCodeRepository
from app.auth.repositories.permission import PermissionInvalidateRepository, PermissionRepository
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.repositories.session import SessionRepository, TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.hash import HashService
from app.auth.services.jwt import AuthJWTManager
from app.auth.services.rbac import AuthRBACManager
from app.auth.services.session import SessionManager
from app.core.configs.app import app_config



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
def jwt_manager(token_blacklist_repository: TokenBlacklistRepository) -> AuthJWTManager:
    return AuthJWTManager(
        jwt_secret=app_config.JWT_SECRET_KEY,
        jwt_algorithm=app_config.JWT_ALGORITHM,
        access_token_expire_minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS,
        token_blacklist=token_blacklist_repository
    )

@pytest.fixture
def rbac_manager() -> AuthRBACManager:
    return AuthRBACManager()

@pytest.fixture
def session_manager(session_repository: SessionRepository) -> SessionManager:
    return SessionManager(session_repository)

