import os
import hashlib
from fastapi import APIRouter, HTTPException, File, UploadFile, BackgroundTasks
# from sqlalchemy.orm import Session
from dotenv import load_dotenv, find_dotenv

from src.services.hash_service import BinaryHashService
from src.services.vector_service import AzureVectorService
from src.services.google_drive_service import GoogleDriveService
from src.services.chunking_service import ChunkingService
from src.services.data_processor import MedicalProcessor
from src.services.pdf_parser import PdfPlumberParser
from src.database.sql_repository import SqlDatabaseRepository
from src.core.medical_orchestrator import MedicalRAGOrchestrator
from src.database.connection import SessionLocal
from src.utils.logger import get_logger

load_dotenv(find_dotenv(), override=True)
logger = get_logger("API")

router = APIRouter(prefix="/v1/medical", tags=["Medical Reports"])

FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
CREDENTIALS_PATH = os.getenv("GDRIVE_CREDENTIALS_PATH")

storage_service = GoogleDriveService(CREDENTIALS_PATH, FOLDER_ID)
vector_service = AzureVectorService()
parser = PdfPlumberParser()
hasher = BinaryHashService()
processor = MedicalProcessor(hasher=hasher)
chunker = ChunkingService()


async def run_background_process(file_name: str, pdf_bytes: bytes, doc_hash: str):
    """Հետին պլանում կատարվող ծանր մշակում"""
    db = SessionLocal()
    try:
        logger.info(f"🚀 Սկսվում է {file_name}-ի ֆոնային մշակումը...")
        orchestrator = MedicalRAGOrchestrator(
            parser=parser,
            processor=processor,
            chunker=chunker,
            storage=storage_service,
            vector_service=vector_service,
            repository=SqlDatabaseRepository(db)
        )
        await orchestrator.handle_report_upload(
            file_name=file_name,
            pdf_bytes=pdf_bytes,
            doc_hash=doc_hash
        )
        logger.info(f"✅ {file_name}-ի մշակումը հաջողությամբ ավարտվեց:")
    except Exception as e:
        logger.error(f"❌ Սխալ ֆոնային մշակման ժամանակ ({file_name}): {str(e)}")
    finally:
        db.close()


@router.post("/upload-medical-report")
async def upload_report(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    logger.info(f"Ստացված է ֆայլ վերբեռնման համար: {file.filename}")

    try:
        pdf_bytes = await file.read()
        doc_hash = hashlib.sha256(pdf_bytes).hexdigest()

        background_tasks.add_task(
            run_background_process, file.filename, pdf_bytes, doc_hash)

        return {
            "status": "processing",
            "message": "Ֆայլը վերբեռնված է և մշակվում է հետին պլանում:",
            "filename": file.filename,
            "hash": doc_hash
        }

    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Վերբեռնման սխալ: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "online", "service": "Medical RAG API"}
