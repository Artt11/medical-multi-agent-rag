import asyncio
from src.database.connection import SessionLocal
from src.services.google_drive_service import GoogleDriveService
from src.services.pdf_parser import PdfPlumberParser
from src.services.data_processor import MedicalProcessor
from src.services.chunking_service import ChunkingService
from src.services.vector_service import AzureVectorService
from src.database.sql_repository import SqlDatabaseRepository
from src.core.medical_orchestrator import MedicalRAGOrchestrator
from src.services.hash_service import BinaryHashService

FOLDER_ID = "15xV7TIwIF2UJW_QXFOXwBwcdLzA0IlBU"
CREDENTIALS_JSON = "gdrive_credentials.json"


async def main():
    print("\n--- 🚀 Մեկնարկում է Medical Data Sync պրոցեսը (JSON Mode) ---")

    db = SessionLocal()

    try:
        hash_service = BinaryHashService()
        storage = GoogleDriveService(CREDENTIALS_JSON, FOLDER_ID)
        repository = SqlDatabaseRepository(db)

        orchestrator = MedicalRAGOrchestrator(
            parser=PdfPlumberParser(),
            processor=MedicalProcessor(hasher=hash_service),
            chunker=ChunkingService(),
            storage=storage,
            vector_service=AzureVectorService(),
            repository=repository
        )

        print(f"🔍 Սկանավորում ենք Google Drive թղթապանակը...")
        drive_files = storage.list_files()

        if not drive_files:
            print("📭 Նոր ֆայլեր չկան կամ թղթապանակը հասանելի չէ։")
            return

        print(f"📂 Գտնվել է {len(drive_files)} PDF ֆայլ։")

        for f in drive_files:
            file_id = f['id']
            file_name = f['name']
            drive_url = f.get('webViewLink', '')

            print(f"\n⚙️ Մշակվում է: {file_name}...")

            try:
                pdf_bytes = storage.download_file_bytes(file_id)
                doc_hash = hash_service.hash_bytes(pdf_bytes)

                result = await orchestrator.process_drive_file(
                    file_id=file_id,
                    file_name=file_name,
                    drive_url=drive_url,
                    doc_hash=doc_hash
                )

                if result:
                    print(f"✅ Հաջողությամբ պահպանվեց SQL-ում։ {file_name}")
                else:
                    print(
                        f"⏭️ Ֆայլն արդեն մշակված է (բաց ենք թողնում)։ {file_name}")

            except Exception as e:
                print(f"❌ Սխալ {file_name}-ի մշակման ժամանակ: {str(e)}")

    except Exception as general_error:
        print(f"🛑 Կրիտիկական սխալ: {str(general_error)}")

    finally:
        db.close()
        print("\n--- ✨ Սինխրոնիզացիան ավարտվեց ---\n")

if __name__ == "__main__":
    asyncio.run(main())
