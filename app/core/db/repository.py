from dataclasses import dataclass
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api.schemas import ListParams, PaginatedResult, Pagination, SortOrder
from app.core.db.base_model import BaseModel


@dataclass
class BaseRepositoryMixin:
    session: AsyncSession

    async def get_list(self, model: type[BaseModel],  params: ListParams)  -> PaginatedResult[BaseModel]:
        query = select(model)
        if params.filters:
            for item in params.filters:
                if isinstance(item.value, list):
                    query = query.where(getattr(model, item.field).in_(item.value))
                else:
                    query = query.where(getattr(model, item.field) == item.value)

        if params.sort:
            for item in params.sort:
                column = getattr(model, item.field)
                query = query.order_by(column.desc() if item.order == SortOrder.desc else column)

        total = await self.session.scalar(select(func.count()).select_from(query.subquery()))
        if total is None:
            total = 0

        query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)
        result = await self.session.execute(query)
        items = result.scalars().all()
        return PaginatedResult(
            items=list(items),
            pagination=Pagination(total=total, page=params.page, page_size=params.page_size),
        )