from dataclasses import dataclass

from app.core.filters.base import BaseFilter
from app.core.filters.condition import FilterOperator


@dataclass
class RoleFilter(BaseFilter):
    name: str | None = None
    security_level: int | None = None
    min_security_level: int | None = None
    max_security_level: int | None = None
    permission_names: list[str] | None = None

    def __post_init__(self):
        self._build_conditions()

    def _build_conditions(self) -> None:
        self.add_condition("name", FilterOperator.CONTAINS, self.name)
        self.add_condition("security_level", FilterOperator.EQ, self.security_level)

        if self.security_level is None:
            self.add_condition("security_level", FilterOperator.GTE, self.min_security_level)
            self.add_condition("security_level", FilterOperator.LTE, self.max_security_level)

        self.add_relation("permissions")

        self.add_condition("permissions.name", FilterOperator.IN, self.permission_names)
