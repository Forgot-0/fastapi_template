from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.convertor import SQLAlchemyFilterConverter
from app.core.filters.base import BaseFilter


T = TypeVar("T")

@dataclass(frozen=True)
class PageResult(Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def next_page(self) -> int | None:
        return self.page + 1 if self.has_next else None

    @property
    def previous_page(self) -> int | None:
        return self.page - 1 if self.has_previous else None


@dataclass
class IRepository(ABC, Generic[T]):
    session: AsyncSession

    async def find_by_filter(self, model: type[T], filters: BaseFilter) -> PageResult[T]:
        stmt = select(model)

        loading_options = SQLAlchemyFilterConverter.build_loading_options(model, filters.loading_config)

        if loading_options:
            stmt = stmt.options(*loading_options)

        conditions = SQLAlchemyFilterConverter.filter_to_sqlalchemy_conditions(model, filters)

        stmt = self.apply_relationship_filters(stmt, filters)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        sort_clauses = SQLAlchemyFilterConverter.get_sort_attributes(model, filters.sort_fields)
        if sort_clauses:
            stmt = stmt.order_by(*sort_clauses)

        stmt = stmt.offset(filters.pagination.offset).limit(filters.pagination.limit)
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return PageResult(
            items=list(items),
            total=total,
            page=filters.pagination.page,
            page_size=filters.pagination.page_size
        )

    async def count_by_filter(self, model: type[T], filters: BaseFilter) -> int:
        stmt = select(func.count()).select_from(model)

        conditions = SQLAlchemyFilterConverter.filter_to_sqlalchemy_conditions(model, filters)
        stmt = self.apply_relationship_filters(stmt, filters)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self.session.execute(stmt)
        return result.scalar_one()

    @abstractmethod
    def apply_relationship_filters(self, stmt: Select, filters: BaseFilter) -> Select:
        ...
