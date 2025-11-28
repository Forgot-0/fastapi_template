from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from tests.integration.auth.factories import RoleFactory


@pytest.mark.integration
@pytest.mark.auth
class TestRoleEndpoints:

    @pytest.mark.asyncio
    async def test_create_role_endpoint(
        self,
        client: AsyncClient,
        admin_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(admin_user)

        response = await client.post(
            "/api/v1/roles/",
            headers=headers,
            json={
                "name": "test_role",
                "description": "Test role",
                "security_level": 3,
                "permissions": []
            }
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_get_roles_endpoint(
        self,
        client: AsyncClient,
        admin_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(admin_user)

        response = await client.get(
            "/api/v1/roles/",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 3

    @pytest.mark.asyncio
    async def test_assign_role_endpoint(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_user: User,
        standard_user: User,
        auth_headers,
    ) -> None:
        test_role = RoleFactory.create(name="assignable", security_level=2)
        db_session.add(test_role)
        await db_session.commit()

        headers = auth_headers(admin_user)

        response = await client.post(
            f"/api/v1/users/{standard_user.id}/roles",
            headers=headers,
            json={"role_name": "assignable"}
        )

        assert response.status_code == 200

