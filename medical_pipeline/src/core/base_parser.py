from abc import ABC, abstractmethod
from typing import Any, Iterable
from src.models.elements import ParsedElement


class IParser(ABC):
    @abstractmethod
    def parse(self, payload: Any) -> Iterable[ParsedElement]:

        pass
