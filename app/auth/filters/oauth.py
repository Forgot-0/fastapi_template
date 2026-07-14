from dataclasses import dataclass

from app.core.filters.base import BaseFilter


@dataclass
class OauthFilter(BaseFilter):

    def build_condition(self) -> None:
        ...
