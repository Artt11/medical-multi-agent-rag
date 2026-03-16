from abc import ABC, abstractmethod
from typing import Iterable

from src.models.document import MedicalDocument


class IDatabaseRepository(ABC):

    @abstractmethod
    def save(self, document: MedicalDocument) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> Iterable[MedicalDocument]:
        raise NotImplementedError
