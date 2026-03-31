import os
from src.services.hash_service import BinaryHashService
from src.services.vector_service import AzureVectorService
# from src.services.azure_storage_service import AzureMedicalStorage
from src.services.google_drive_service import GoogleDriveService
from src.services.chunking_service import ChunkingService
from src.services.data_processor import MedicalProcessor
from src.services.pdf_parser import PdfPlumberParser
from src.database.sql_repository import SqlDatabaseRepository
from src.core.medical_orchestrator import MedicalRAGOrchestrator
from src.database.connection import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
import hashlib
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

router = APIRouter(prefix="/v1/medical", tags=["Medical Reports"])

FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
CREDENTIALS_PATH = os.getenv("GDRIVE_CREDENTIALS_PATH")

storage_service = GoogleDriveService(CREDENTIALS_PATH, FOLDER_ID)
# storage_service = AzureMedicalStorage()
vector_service = AzureVectorService()
parser = PdfPlumberParser()
hasher = BinaryHashService()
processor = MedicalProcessor(hasher=hasher)
chunker = ChunkingService()


@router.post("/upload-medical-report")
async def upload_report(file: UploadFile = File(...), db: Session = Depends(get_db)):

    try:
        pdf_bytes = await file.read()
        file_name = file.filename

        doc_hash = hashlib.sha256(pdf_bytes).hexdigest()

        orchestrator = MedicalRAGOrchestrator(
            parser=parser,
            processor=processor,
            chunker=chunker,
            storage=storage_service,
            vector_service=vector_service,
            repository=SqlDatabaseRepository(db)
        )

        doc, pdf_url = await orchestrator.handle_report_upload(
            file_name=file_name,
            pdf_bytes=pdf_bytes,
            doc_hash=doc_hash
        )

        return {
            "status": "success",
            "extracted_info": {
                "patient": doc.patient.name,
                "social_card": doc.patient.social_card,
                "chunks_created": len(doc.chunks)
            },
            "urls": {"pdf": pdf_url}
        }

    except Exception as e:
        import traceback
        print(f" API Error: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Pipeline error: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "online", "service": "Medical RAG Orchestrator"}
