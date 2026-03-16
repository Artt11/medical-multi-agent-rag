from abc import ABC, abstractmethod
from typing import List
from src.core.schemas import MedicalSearchQuery
from src.models.document import MedicalChunk


class IBaseRetriever(ABC):
    @abstractmethod
    def search(self, params: MedicalSearchQuery) -> List[MedicalChunk]:
        pass
