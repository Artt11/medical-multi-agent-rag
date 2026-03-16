from abc import ABC, abstractmethod
from typing import List
from src.models.document import MedicalDocument, MedicalChunk


class IChunkingService(ABC):
    @abstractmethod
    def create_chunks(self, doc: MedicalDocument) -> List[MedicalChunk]:
        pass
