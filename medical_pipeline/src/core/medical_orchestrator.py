from src.core.base_parser import IParser
from src.core.base_processor import IProcessor
from src.core.base_storage import IStorageService
from src.core.base_vector_service import IVectorService
from src.core.base_repository import IDatabaseRepository
from src.models.document import MedicalDocument
from src.core.base_chunking import IChunkingService
from src.utils.logger import get_logger

logger = get_logger("PIPELINE")

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

    async def process_drive_file(self, file_id: str, file_name: str, drive_url: str, doc_hash: str):
        logger.debug(f"Downloading from Drive: {file_name}")
        pdf_bytes = self.storage.download_file_bytes(file_id)
        
        logger.debug(f"Parsing PDF: {file_name}")
        elements = self.parser.parse(pdf_bytes)
        
        logger.debug(f"GPT Processing: {file_name}")
        doc: MedicalDocument = self.processor.process(file_name, elements)
        doc.hash = doc_hash
        
        logger.debug(f"Generating Chunks: {file_name}")
        doc.chunks = self.chunker.create_chunks(doc)

        self.repository.save(document=doc, source_url=drive_url)

        if doc.chunks:
            for chunk in doc.chunks:
                chunk.metadata.update({
                    "doc_hash": doc_hash,
                    "blob_url": drive_url,
                    "patient_db_id": str(doc.patient.patient_id or "unknown")
                })
            logger.debug(f"Vector Indexing chunks for {file_name}")
            self.vector_service.index_chunks(doc.chunks)
        else:
            logger.warning(
                f"No chunks generated for {file_name}. Skipping indexing.")

        logger.info(f"Request Completed for {file_name}")
        return doc, drive_url
