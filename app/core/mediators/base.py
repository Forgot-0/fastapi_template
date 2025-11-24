
from abc import ABC
from dataclasses import dataclass

from app.core.mediators.command import CommandMediator
from app.core.mediators.query import QueryMediator


@dataclass(eq=False)
class BaseMediator(CommandMediator, QueryMediator, ABC):
    ...
