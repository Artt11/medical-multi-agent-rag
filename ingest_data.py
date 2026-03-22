import os
import sys
import asyncio
import hashlib
from dotenv import load_dotenv, find_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
pipeline_path = os.path.join(current_dir, "medical_pipeline")
sys.path.append(pipeline_path)

load_dotenv(find_dotenv(), override=True)

try:
    from medical_pipeline.src.database.connection import SessionLocal
    from medical_pipeline.src.core.medical_orchestrator import MedicalRAGOrchestrator
    from medical_pipeline.src.database.sql_repository import SqlDatabaseRepository
    from medical_pipeline.src.services.pdf_parser import PdfPlumberParser
    from medical_pipeline.src.services.data_processor import MedicalProcessor
    from medical_pipeline.src.services.chunking_service import ChunkingService
    from medical_pipeline.src.services.azure_storage_service import AzureMedicalStorage
    from medical_pipeline.src.services.vector_service import AzureVectorService
    from medical_pipeline.src.services.hash_service import BinaryHashService

    print("Բոլոր մոդուլները հաջողությամբ բեռնվեցին:")
except ImportError as e:
    print(f" Import-ի սխալ: {e}")
    print(f"Փորձում էի փնտրել այստեղ: {pipeline_path}")
    sys.exit(1)


async def ingest_medical_documents():
    print("\n Սկսում ենք PDF-ների ավտոմատ մշակումը...\n")

    storage_service = AzureMedicalStorage()
    vector_service = AzureVectorService()
    parser = PdfPlumberParser()
    hasher = BinaryHashService()
    processor = MedicalProcessor(hasher=hasher)
    chunker = ChunkingService()

    db = SessionLocal()
    repository = SqlDatabaseRepository(db)

    orchestrator = MedicalRAGOrchestrator(
        parser=parser,
        processor=processor,
        chunker=chunker,
        storage=storage_service,
        vector_service=vector_service,
        repository=repository
    )

    pdf_folder = os.path.join(pipeline_path, "data_pdf")

    if not os.path.exists(pdf_folder):
        pdf_folder = os.path.join(current_dir, "data_pdf")

    if not os.path.exists(pdf_folder):
        print(f"Չեմ գտնում PDF-ների թղթապանակը ({pdf_folder})")
        return

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    print(f"Գտնվել է {len(pdf_files)} ֆայլ '{pdf_folder}' թղթապանակում\n")

    for file_name in pdf_files:
        file_path = os.path.join(pdf_folder, file_name)
        print(f"Մշակվում է: {file_name}...")

        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()

            doc_hash = hashlib.sha256(pdf_bytes).hexdigest()

            doc, pdf_url = await orchestrator.handle_report_upload(
                file_name=file_name,
                pdf_bytes=pdf_bytes,
                doc_hash=doc_hash
            )

            print(
                f"Հաջողությամբ պահվեց: {doc.patient.name} (Chunks: {len(doc.chunks)})")

        except Exception as e:
            print(f"ՍԽԱԼ '{file_name}': {e}")

    db.close()
    print("\nԱվարտված է: Այժմ կարող ես հարցեր տալ չաթին:")

if __name__ == "__main__":
    asyncio.run(ingest_medical_documents())
