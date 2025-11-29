import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from app.auth.repositories.role import  RoleRepository
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserJWTData
from app.auth.services.hash import HashService
from app.auth.services.jwt import JWTManager
from tests.auth.integration.factories import UserFactory


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