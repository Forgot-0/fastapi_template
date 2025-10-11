from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession



@dataclass
class RoleRepository:
    session: AsyncSession

