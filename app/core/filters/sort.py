from dataclasses import dataclass
from enum import StrEnum


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class SortField:
    field: str
    direction: SortDirection = SortDirection.ASC

    @property
    def is_ascending(self) -> bool:
        return self.direction == SortDirection.ASC

    @property
    def is_descending(self) -> bool:
        return self.direction == SortDirection.DESC

