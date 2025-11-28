from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.permission import Permission
from app.auth.models.user import User


@pytest.mark.integration
@pytest.mark.auth
class TestPermissionEndpoints:

    @pytest.mark.asyncio
    async def test_create_permission_endpoint(
        self,
        client: AsyncClient,
        admin_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(admin_user)

        response = await client.post(
            "/api/v1/permissions/",
            headers=headers,
            json={"name": "test:permission"}
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_get_permissions_endpoint(
        self,
        client: AsyncClient,
        admin_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(admin_user)

        response = await client.get(
            "/api/v1/permissions/",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_delete_permission_endpoint(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_user: User,
        auth_headers,
    ) -> None:
        perm = Permission(name="deletable:test")
        db_session.add(perm)
        await db_session.commit()

        headers = auth_headers(admin_user)

        response = await client.delete(
            "/api/v1/permissions/deletable:test",
            headers=headers,
        )

        assert response.status_code == 204

