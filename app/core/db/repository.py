from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import hashlib
from typing import Any, Awaitable, Callable, Generic, ParamSpec, TypeVar

import orjson
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.base_model import SoftDeleteMixin
from app.core.db.convertor import SQLAlchemyFilterConverter
from app.core.filters.base import BaseFilter


T = TypeVar("T")
P = ParamSpec("P")

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
        if isinstance(model, SoftDeleteMixin):
            stmt = model.select_not_deleted()
        else:
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

B = TypeVar("B", bound=BaseModel)


@dataclass
class CacheRepository:
    redis: Redis
    _LIST_VERSION_KEY: str = field(kw_only=True, init=False)

    def _serialize_args_kwargs(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> bytes:
        args_repr = "|".join(repr(a) for a in args)
        kwargs_items = sorted(kwargs.items())
        kwargs_repr = "|".join(f"{k}={repr(v)}" for k, v in kwargs_items)
        combined = f"args:{args_repr};kwargs:{kwargs_repr}"
        return combined.encode("utf-8")

    async def _build_key(
        self,
        type_model: type[B],
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> str:
        version = await self._get_list_version()

        func_mod = getattr(func, "__module__", "unknown")
        func_qname = getattr(func, "__qualname__", "none")
        serialized = self._serialize_args_kwargs(args, kwargs)
        digest = hashlib.sha256(serialized).hexdigest()
        return f"cache:{type_model.__name__}:ver={version}:{func_mod}.{func_qname}:{digest}"

    async def cache(
        self,
        type_model: type[B],
        func: Callable[P, Awaitable[B]],
        ttl: int=60, *args, **kwargs
    ) -> B:
        key = await self._build_key(type_model, func, args, kwargs)
        data = await self.redis.get(key)

        if data is None:
            data = await func(*args, **kwargs)
            cahed_data = data.model_dump_json()
            await self.redis.setex(key, time=ttl, value=cahed_data)
            return data
        return type_model.model_validate_json(data)

    async def cache_paginated(
        self, type_model: type[B],
        func: Callable[P, Awaitable[PageResult[B]]],
        ttl: int=60, *args, **kwargs
    ) -> PageResult[B]:
        key = await self._build_key(type_model, func, args, kwargs)

        data = await self.redis.get(key)
        if data is None:
            data = await func(*args, **kwargs)
            payload = {
                "items": [item.model_dump_json() for item in data.items],
                "total": data.total,
                "page": data.page,
                "page_size": data.page_size
            }
            await self.redis.setex(key, time=ttl, value=orjson.dumps(payload))
            return data

        data = orjson.loads(data)
        return PageResult(
            items=[type_model.model_validate_json(item) for item in data.get("items", [])],
            total=data["total"],
            page=data["page"],
            page_size=data["page_size"]
        )

    async def invadate_cache(self, *keys: str) -> None:
        if keys:
            await self.redis.delete(*keys)
        await self.redis.incrby(self._LIST_VERSION_KEY)

    async def _get_list_version(self) -> int:
        v = await self.redis.get(self._LIST_VERSION_KEY)
        return int(v) if v else 0

