from datetime import timedelta
import pytest
from passlib.context import CryptContext

from app.auth.services.hash import HashService
from app.auth.services.jwt import JWTManager
from app.core.utils import fromtimestamp, now_utc



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
