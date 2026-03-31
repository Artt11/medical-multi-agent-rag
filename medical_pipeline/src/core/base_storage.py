from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IStorageService(ABC):

    @abstractmethod
    def upload_medical_pair(self, file_hash: str, pdf_bytes: bytes, doc_data: dict) -> str:
        """Նախկին մեթոդը. կարող ենք պահել API-ի միջոցով վերբեռնումների համար"""
        pass

    @abstractmethod
    def list_files(self) -> List[Dict[str, Any]]:
        """
        ՆՈՐ ՏՐԱՄԱԲԱՆՈՒԹՅՈՒՆ. Վերադարձնում է պահոցում առկա ֆայլերի ցուցակը:
        Օրինակ՝ [{'id': '123', 'name': 'report.pdf', 'url': 'https://...'}]
        """
        pass

    @abstractmethod
    def download_file_bytes(self, file_id: str) -> bytes:
        """
        ՆՈՐ ՏՐԱՄԱԲԱՆՈՒԹՅՈՒՆ. Կարդում է ֆայլը ըստ ID-ի և վերադարձնում 
        որպես բայթերի հոսք (առանց սերվերում պահելու)
        """
        pass
