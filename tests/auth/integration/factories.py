from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from app.auth.models.permission import Permission
from app.auth.models.role import Role
from app.auth.models.session import Session
from app.auth.models.user import User
from app.core.utils import now_utc


class UserFactory:

    @staticmethod
    def create(
        email: str | None = None,
        username: str | None = None,
        password_hash: str | None = None,
        is_active: bool = True,
        is_verified: bool = False,
        roles: set[Role] | None = None,
        permissions: set[Permission] | None = None,
        **kwargs: Any
    ) -> User:
        user = User(
            email=email or f"test_{uuid4().hex[:8]}@example.com",
            username=username or f"user{uuid4().hex[:8]}",
            password_hash=password_hash,
            is_active=is_active,
            is_verified=is_verified,
            roles=roles or set(),
            permissions=permissions or set(),
            **kwargs
        )
        return user

    @staticmethod
    def create_verified(
        email: str | None = None,
        username: str | None = None,
        roles: set[Role] | None = None,
        permissions: set[Permission] | None = None,
        **kwargs: Any
    ) -> User:
        return UserFactory.create(
            email=email,
            username=username,
            is_verified=True,
            roles=roles,
            permissions=permissions,
            **kwargs
        )

    @staticmethod
    def create_with_role(
        role: Role,
        email: str | None = None,
        username: str | None = None,
        **kwargs: Any
    ) -> User:
        return UserFactory.create(
            email=email,
            username=username,
            roles={role},
            **kwargs
        )


class RoleFactory:
    @staticmethod
    def create(
        name: str | None = None,
        description: str | None = None,
        security_level: int = 1,
        permissions: set[Permission] | None = None,
        **kwargs: Any
    ) -> Role:
        role = Role(
            name=name or f"role_{uuid4().hex[:8]}",
            description=description or "Test role",
            security_level=security_level,
            permissions=permissions or set(),
            **kwargs
        )
        return role

    @staticmethod
    def create_admin_role() -> Role:
        return RoleFactory.create(
            name="admin",
            description="Admin role",
            security_level=9
        )


class PermissionFactory:
    @staticmethod
    def create(
        name: str | None = None,
        **kwargs: Any
    ) -> Permission:
        permission = Permission(
            name=name or f"permission_{uuid4().hex[:8]}",
            **kwargs
        )
        return permission

    @staticmethod
    def create_multiple(count: int) -> list[Permission]:
        return [PermissionFactory.create() for _ in range(count)]


class SessionFactory:
    @staticmethod
    def create(
        user_id: int,
        device_id: str | None = None,
        user_agent: str | None = None,
        is_active: bool = True,
        last_activity: datetime | None = None,
        **kwargs: Any
    ) -> Session:
        session = Session(
            user_id=user_id,
            device_id=device_id or uuid4().hex,
            device_info=b'{"browser": "Chrome", "os": "Windows"}',
            user_agent=user_agent or "Mozilla/5.0",
            is_active=is_active,
            last_activity=last_activity or now_utc(),
            **kwargs
        )
        return session

    @staticmethod
    def create_expired(
        user_id: int,
        **kwargs: Any
    ) -> Session:
        return SessionFactory.create(
            user_id=user_id,
            last_activity=now_utc() - timedelta(days=30),
            is_active=False,
            **kwargs
        )


class TokenFactory:
    @staticmethod
    def create_access_token_payload(
        user_id: int,
        device_id: str | None = None,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        security_level: int = 1,
        exp_minutes: int = 30,
    ) -> dict[str, Any]:
        now = now_utc()
        return {
            "type": "access",
            "sub": str(user_id),
            "lvl": security_level,
            "did": device_id or uuid4().hex,
            "jti": str(uuid4()),
            "exp": (now + timedelta(minutes=exp_minutes)).timestamp(),
            "iat": now.timestamp(),
            "roles": roles or [],
            "permissions": permissions or [],
        }

    @staticmethod
    def create_refresh_token_payload(
        user_id: int,
        device_id: str | None = None,
        exp_days: int = 7,
    ) -> dict[str, Any]:
        now = now_utc()
        return {
            "type": "refresh",
            "sub": str(user_id),
            "lvl": 1,
            "did": device_id or uuid4().hex,
            "jti": str(uuid4()),
            "exp": (now + timedelta(days=exp_days)).timestamp(),
            "iat": now.timestamp(),
        }


class CommandFactory:
    @staticmethod
    def create_register_command(
        username: str | None = None,
        email: str | None = None,
        password: str = "TestPass123!",
    ) -> dict[str, Any]:
        return {
            "username": username or f"user{uuid4().hex[:8]}",
            "email": email or f"test_{uuid4().hex[:8]}@example.com",
            "password": password,
            "password_repeat": password,
        }

    @staticmethod
    def create_login_command(
        username: str,
        password: str = "TestPass123!",
        user_agent: str = "Mozilla/5.0",
    ) -> dict[str, Any]:
        return {
            "username": username,
            "password": password,
            "user_agent": user_agent,
        }
