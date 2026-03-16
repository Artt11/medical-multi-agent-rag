from abc import ABC, abstractmethod
from typing import Iterable, Protocol
from src.models.elements import ParsedElement
from src.models.document import MedicalDocument


class SupportsHashing(Protocol):
    def hash_bytes(self, data: bytes) -> str:
        ...


class IProcessor(ABC):
    @abstractmethod
    def process(self, source_name: str, elements: Iterable[ParsedElement]) \
            -> MedicalDocument:

        pass
