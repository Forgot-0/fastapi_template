from dataclasses import dataclass
from datetime import datetime

from app.core.filters.base import BaseFilter
from app.core.filters.condition import FilterOperator
from app.core.filters.loading_strategy import LoadingStrategyType


@dataclass
class UserFilter(BaseFilter):
    email: str | None = None
    username: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    is_deleted: bool | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    has_oauth_accounts: bool | None = None
    has_sessions: bool | None = None
    role_names: list[str] | None = None
    permission_names: list[str] | None = None

    def __post_init__(self):
        self._build_conditions()

    def _build_conditions(self) -> None:
        self.add_condition("is_active", FilterOperator.EQ, self.is_active)
        self.add_condition("is_verified", FilterOperator.EQ, self.is_verified)
        if self.is_deleted is not None:
            self.add_condition(
                "deleted_at",
                FilterOperator.IS_NOT_NULL if self.is_deleted else FilterOperator.IS_NULL,
                None
            )

        self.add_condition("email", FilterOperator.CONTAINS, self.email)

        self.add_condition("username", FilterOperator.CONTAINS, self.username)

        self.add_condition("created_at", FilterOperator.GTE, self.created_after)

        self.add_condition("created_at", FilterOperator.LTE, self.created_before)

        self.add_condition("updated_at", FilterOperator.GTE, self.updated_after)
        self.add_condition("updated_at", FilterOperator.LTE, self.updated_before)

        self.add_relation("oauth_accounts")
        self.add_relation("sessions")
        self.add_relation("permissions")
        self.add_relation("roles", LoadingStrategyType.SELECTIN, "permissions")

        if self.has_oauth_accounts is not None:
            operator = FilterOperator.IS_NOT_NULL_FROM if self.has_oauth_accounts else FilterOperator.IS_NULL_FROM
            self.add_condition("oauth_accounts", operator, None)

        if self.has_sessions is not None:
            operator = FilterOperator.IS_NOT_NULL_FROM if self.has_sessions else FilterOperator.IS_NULL_FROM
            self.add_condition("sessions", operator, None)

        self.add_condition("roles.name", FilterOperator.IN, self.role_names)

        self.add_condition("permissions.name", FilterOperator.IN, self.permission_names)

