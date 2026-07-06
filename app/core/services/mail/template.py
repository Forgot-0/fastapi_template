from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


class BaseTemplate(ABC):
    _env: Environment | None = None

    @property
    def env(self) -> Environment:
        if self._env is None:
            self._env = Environment(
                loader=FileSystemLoader(self._get_dir()), autoescape=True
            )
        return self._env

    @abstractmethod
    def _get_dir(self) -> Path: ...

    @abstractmethod
    def _get_name(self) -> str: ...

    def _get_data(self) -> dict[str, Any]:
        return {k: v for k, v in vars(self).items() if not k.startswith("_") and not k.startswith("__")}

    def render(self) -> str:
        return self.env.get_template(self._get_name()).render(self._get_data())

