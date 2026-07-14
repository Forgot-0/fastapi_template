import pytest
from dishka import AsyncContainer

from app.auth.repositories.oauth import OAuthCodeRepository
from app.auth.repositories.permission import PermissionInvalidateRepository, PermissionRepository
from app.auth.repositories.role import RoleInvalidateRepository, RoleRepository
from app.auth.repositories.session import SessionRepository, TokenBlacklistRepository
from app.auth.repositories.user import UserRepository
from app.auth.services.hash import HashService
from app.auth.services.jwt import AuthJWTManager
from app.auth.services.rbac import AuthRBACManager
from app.auth.services.session import SessionManager


@pytest.fixture
async def user_repository(request_container: AsyncContainer) -> UserRepository:
    return await request_container.get(UserRepository)

@pytest.fixture
async def role_repository(request_container: AsyncContainer) -> RoleRepository:
    return await request_container.get(RoleRepository)

@pytest.fixture
async def permission_repository(request_container: AsyncContainer) -> PermissionRepository:
    return await request_container.get(PermissionRepository)

@pytest.fixture
async def session_repository(request_container: AsyncContainer) -> SessionRepository:
    return await request_container.get(SessionRepository)


@pytest.fixture
async def token_blacklist_repository(di_container: AsyncContainer) -> TokenBlacklistRepository:
    return await di_container.get(TokenBlacklistRepository)


@pytest.fixture
async def role_blacklist(di_container: AsyncContainer) -> RoleInvalidateRepository:
    return await di_container.get(RoleInvalidateRepository)


@pytest.fixture
async def permission_blacklist(di_container: AsyncContainer) -> PermissionInvalidateRepository:
    return await di_container.get(PermissionInvalidateRepository)

@pytest.fixture
async def oauth_code_repository(di_container: AsyncContainer) -> OAuthCodeRepository:
    return await di_container.get(OAuthCodeRepository)


@pytest.fixture
async def hash_service(di_container: AsyncContainer) -> HashService:
    return await di_container.get(HashService)

@pytest.fixture
async def auth_jwt_manager(request_container: AsyncContainer) -> AuthJWTManager:
    return await request_container.get(AuthJWTManager)

@pytest.fixture
async def rbac_manager(di_container: AsyncContainer) -> AuthRBACManager:
    return await di_container.get(AuthRBACManager)

@pytest.fixture
async def session_manager(request_container: AsyncContainer) -> SessionManager:
    return await request_container.get(SessionManager)
