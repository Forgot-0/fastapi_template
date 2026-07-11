from dataclasses import dataclass


@dataclass(frozen=True)
class PaginatedResponseDto[TDto]:
    items: list[TDto]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    next_page: int | None
    previous_page: int | None

