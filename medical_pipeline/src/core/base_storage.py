from abc import ABC, abstractmethod


class IStorageService(ABC):

    @abstractmethod
    def upload_medical_pair(self, file_hash: str, pdf_bytes: bytes, doc_data: dict) -> str:

        pass
