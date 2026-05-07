import os
from src.database.connection import SessionLocal
from src.database.models import PatientModel, MedicalExamModel
from src.services.vector_service import AzureVectorService
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential


def cleanup():
    print("--- 🧹 Սկսվում է համակարգի ամբողջական մաքրումը ---")

    # 1. Մաքրում ենք SQL տվյալները
    db = SessionLocal()
    try:
        print("🗑️ Մաքրվում են SQL աղյուսակները (Medical Exams & Patients)...")
        # Ջնջում ենք բոլոր գրառումները
        db.query(MedicalExamModel).delete()
        db.query(PatientModel).delete()
        db.commit()
        print("✅ SQL աղյուսակները դատարկ են:")
    except Exception as e:
        db.rollback()
        print(f"❌ SQL սխալ: {e}")
    finally:
        db.close()

    # 2. Մաքրում ենք Azure Index-ը
    try:
        print("🗑️ Ջնջվում է Azure Search ինդեքսը...")
        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        key = os.getenv("AZURE_SEARCH_KEY")
        index_name = "medical-index"

        client = SearchIndexClient(endpoint, AzureKeyCredential(key))
        client.delete_index(index_name)
        print(f"✅ Ինդեքսը '{index_name}' ջնջվեց:")

        # Վերստեղծում ենք թարմ ու դատարկ ինդեքս
        print("🏗️ Ստեղծվում է նոր և ճիշտ կառուցվածքով ինդեքս...")
        vector_service = AzureVectorService(index_name=index_name)
        vector_service.create_index()
        print("✅ Azure-ը պատրաստ է նոր տվյալների համար:")

    except Exception as e:
        print(f"❌ Azure սխալ: {e}")

    print("\n--- ✨ Համակարգը մաքուր է: Հիմա կարող եք աշխատեցնել sync_drive.py ---")


if __name__ == "__main__":
    cleanup()
