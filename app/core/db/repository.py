from dataclasses import dataclass
from typing import Literal

from sqlalchemy import Column, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, subqueryload

from app.core.api.schemas import ListParams, PaginatedResult, Pagination, SortOrder
from app.core.db.base_model import BaseModel


@dataclass
class BaseRepositoryMixin:
    session: AsyncSession

    async def get_list(
        self,
        model: type[BaseModel],
        params: ListParams,
        relations: dict[Literal["select", "joined", "subquery"], list[str]] | None = None,
    )  -> PaginatedResult[BaseModel]:
        query = select(model)
        if params.filters:
            for filter_params in params.filters:
                if isinstance(filter_params.value, list):
                    query = query.where(getattr(model, filter_params.field).in_(filter_params.value))
                else:
                    query = query.where(getattr(model, filter_params.field) == filter_params.value)

        query = self._load_relations(query=query, relations=relations, model=model)

        if params.sort:
            for sort_params in params.sort:
                column: Column = getattr(model, sort_params.field)
                query = query.order_by(column.desc() if sort_params.order == SortOrder.DESC else column)

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

    def _load_relations(
        self,
        query: Select,
        model: type[BaseModel],
        relations: dict[Literal["select", "joined", "subquery"], list[str]] | None = None,
    ) -> Select:

        if not relations:
            return query

        loader_map = {
            "select": selectinload,
            "joined": joinedload,
            "subquery": subqueryload,
        }

        loader_method_name = {
            "select": "selectinload",
            "joined": "joinedload",
            "subquery": "subqueryload",
        }

        for strategy, rels in relations.items():
            if strategy not in loader_map:
                raise ValueError(f"Unknown loading strategy: {strategy}")

            for relation_path in rels:
                parts = relation_path.split(".")
                current_model = model
                loader = None

                for i, part in enumerate(parts):
                    try:
                        attr = getattr(current_model, part)
                    except AttributeError as e:
                        raise AttributeError(f"Model {current_model.__name__} has no attribute '{part}'") from e

                    if loader is None:
                        loader = loader_map[strategy](attr)
                    else:
                        method = getattr(loader, loader_method_name[strategy])
                        loader = method(attr)

                    prop = getattr(attr, "property", None)
                    if prop is None or not hasattr(prop, "mapper"):
                        if i < len(parts) - 1:
                            raise ValueError(f"Attribute '{part}' of {current_model.__name__} is not a relationship "
                                                f"but path has more parts: '{relation_path}'")
                        related_class = None
                    else:
                        related_class = prop.mapper.class_

                    if related_class:
                        current_model = related_class

                if loader is not None:
                    query = query.options(loader)

        return query
