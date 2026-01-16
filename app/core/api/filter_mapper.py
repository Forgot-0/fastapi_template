from app.core.filters.sort import SortDirection, SortField


class FilterMapper:
    @staticmethod
    def parse_sort_string(sort_string: str | None) -> list[SortField]:
        if not sort_string:
            return []

        sort_fields = []
        for part in sort_string.split(","):
            part = part.strip()
            if not part:
                continue

            if ":" in part:
                field, direction = part.split(":", 1)
                direction = direction.strip().lower()
                sort_direction = (
                    SortDirection.DESC if direction == "desc"
                    else SortDirection.ASC
                )
            else:
                field = part
                sort_direction = SortDirection.ASC

            sort_fields.append(SortField(field=field.strip(), direction=sort_direction))

        return sort_fields
