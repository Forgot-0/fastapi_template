from dataclasses import dataclass

from app.core.filters.base import BaseFilter
from app.core.filters.condition import FilterOperator


@dataclass
class PermissionFilter(BaseFilter):
    name: str | None = None

    def buil_condition(self) -> None:
        self.add_condition("name", FilterOperator.CONTAINS, self.name)
