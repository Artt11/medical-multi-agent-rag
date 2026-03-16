from abc import ABC, abstractmethod
from typing import List
from src.models.document import MedicalChunk


class IVectorService(ABC):

    @abstractmethod
    def create_index(self) -> None:
        pass

    @abstractmethod
    def index_chunks(self, chunks: List[MedicalChunk]) -> None:
        pass
