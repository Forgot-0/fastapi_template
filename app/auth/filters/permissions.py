from dataclasses import dataclass

from app.core.filters.base import BaseFilter
from app.core.filters.condition import FilterOperator


@dataclass
class PermissionFilter(BaseFilter):
    name: str | None = None

    def __post_init__(self) -> None:
        self._build_conditions()

    def _build_conditions(self) -> None:
        self.add_condition("name", FilterOperator.CONTAINS, self.name)
