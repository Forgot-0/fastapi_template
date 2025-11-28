
from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from tests.integration.auth.factories import SessionFactory


@pytest.mark.integration
@pytest.mark.auth
class TestSessionEndpoints:

    @pytest.mark.asyncio
    async def test_get_sessions_endpoint(
        self,
        client: AsyncClient,
        admin_user: User,
        auth_headers,
    ) -> None:
        headers = auth_headers(admin_user)

        response = await client.get(
            "/api/v1/sessions/",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_deactivate_session_endpoint(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        standard_user: User,
        auth_headers,
    ) -> None:
        test_session = SessionFactory.create(user_id=standard_user.id)
        db_session.add(test_session)
        await db_session.commit()

        headers = auth_headers(standard_user)

        response = await client.delete(
            f"/api/v1/sessions/{test_session.id}",
            headers=headers
        )

        assert response.status_code == 204