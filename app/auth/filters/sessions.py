from dataclasses import dataclass
from datetime import datetime

from app.core.filters.base import BaseFilter
from app.core.filters.condition import FilterOperator


@dataclass
class SessionFilter(BaseFilter):
    user_id: int | None = None
    device_id: str | None = None
    last_activity_after: datetime | None = None
    last_activity_before: datetime | None = None
    is_active: bool | None = None

    def __post_init__(self):
        self._build_conditions()

    def _build_conditions(self) -> None:
        self.add_condition("user_id", FilterOperator.EQ, self.user_id)
        self.add_condition("device_id", FilterOperator.EQ, self.device_id)
        self.add_condition("is_active", FilterOperator.EQ, self.is_active)

        self.add_condition("last_activity", FilterOperator.GTE, self.last_activity_after)
        self.add_condition("last_activity", FilterOperator.LTE, self.last_activity_before)
