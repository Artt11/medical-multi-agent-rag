from src.core.base_parser import IParser
from src.core.base_processor import IProcessor
from src.core.base_storage import IStorageService
from src.core.base_vector_service import IVectorService
from src.core.base_repository import IDatabaseRepository
from src.models.document import MedicalDocument
from src.core.base_chunking import IChunkingService


class MedicalRAGOrchestrator:
    def __init__(
        self,
        parser: IParser,
        processor: IProcessor,
        chunker: IChunkingService,
        storage: IStorageService,
        vector_service: IVectorService,
        repository: IDatabaseRepository
    ):
        self.parser = parser
        self.processor = processor
        self.chunker = chunker
        self.storage = storage
        self.vector_service = vector_service
        self.repository = repository

    async def handle_report_upload(self, file_name: str, pdf_bytes: bytes, doc_hash: str):
        elements = self.parser.parse(pdf_bytes)

        doc: MedicalDocument = self.processor.process(file_name, elements)
        doc.hash = doc_hash

        doc.chunks = self.chunker.create_chunks(doc)

        self.repository.save(doc)

        pdf_url = self.storage.upload_medical_pair(
            file_hash=doc_hash,
            pdf_bytes=pdf_bytes,
            doc_data=doc.model_dump(mode='json')
        )

        if doc.chunks:
            for chunk in doc.chunks:
                chunk.metadata.update({
                    "doc_hash": doc_hash,
                    "blob_url": pdf_url,
                    "patient_db_id": str(doc.patient.patient_id or "unknown")
                })

            self.vector_service.index_chunks(doc.chunks)
        else:
            print("Warning: No chunks generated. Skipping indexing.")

        return doc, pdf_url
