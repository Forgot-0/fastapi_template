import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from app.auth.services.session import SessionManager


@pytest.mark.unit
@pytest.mark.auth
class TestSessionManager:

    @pytest.mark.asyncio
    async def test_create_session(
        self,
        standard_user: User,
        session_manager: SessionManager,
    ) -> None:
        new_session = await session_manager.get_or_create_session(
            user_id=standard_user.id,
            user_agent="Chrome/100.0"
        )

        assert new_session.user_id == standard_user.id
        assert new_session.is_active is True
        assert new_session.device_id is not None

    @pytest.mark.asyncio
    async def test_get_existing_session(
        self,
        db_session: AsyncSession,
        standard_user: User,
        session_manager: SessionManager,
    ) -> None:
        session1 = await session_manager.get_or_create_session(
            user_id=standard_user.id,
            user_agent="Chrome/100.0"
        )
        await db_session.commit()

        session2 = await session_manager.get_or_create_session(
            user_id=standard_user.id,
            user_agent="Chrome/100.0"
        )

        assert session1.device_id == session2.device_id
        assert session1.id == session2.id

    @pytest.mark.asyncio
    async def test_different_devices_different_sessions(
        self,
        standard_user: User,
        session_manager: SessionManager,
    ) -> None:

        session1 = await session_manager.get_or_create_session(
            user_id=standard_user.id,
            user_agent="Chrome/100.0"
        )

        session2 = await session_manager.get_or_create_session(
            user_id=standard_user.id,
            user_agent="Firefox/90.0"
        )

        assert session1.device_id != session2.device_id

    @pytest.mark.asyncio
    async def test_session_device_id_generation(
        self,
        standard_user: User,
        session_manager: SessionManager
    ) -> None:

        session = await session_manager.get_or_create_session(
            user_id=standard_user.id,
            user_agent="Chrome/100.0 on Windows"
        )

        assert session.device_id is not None
        assert len(session.device_id) > 10
        assert session.device_info is not None

    @pytest.mark.asyncio
    async def test_session_updates_activity(
        self,
        db_session: AsyncSession,
        standard_user: User,
        session_manager: SessionManager
    ) -> None:

        session1 = await session_manager.get_or_create_session(
            user_id=standard_user.id,
            user_agent="Chrome/100.0"
        )
        await db_session.commit()

        old_activity = session1.last_activity

        await asyncio.sleep(0.1)

        session2 = await session_manager.get_or_create_session(
            user_id=standard_user.id,
            user_agent="Chrome/100.0"
        )

        assert session2.last_activity > old_activity
