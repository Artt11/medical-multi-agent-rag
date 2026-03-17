from sqlalchemy import desc
from src.database.connection import SessionLocal
from src.database.models import MedicalExamModel
from src.services.storage_service import download_blob_to_file


class DocumentManager:

    @staticmethod
    def get_latest_report_by_patient(patient_internal_id: int) -> dict:

        if not patient_internal_id:
            return None

        db = SessionLocal()
        try:
            exam = db.query(MedicalExamModel).filter(
                MedicalExamModel.patient_id == patient_internal_id
            ).order_by(desc(MedicalExamModel.exam_date)).first()

            if not exam or not exam.source_file:
                print(
                    f"--- 📂 LOG: No report found for patient ID {patient_internal_id} ---")
                return None

            local_path = download_blob_to_file(exam.source_file)

            if local_path:
                return {
                    "path": local_path,
                    "name": exam.source_file
                }

            return None

        except Exception as e:
            print(f"---  DocumentManager Error: {str(e)} ---")
            return None
        finally:
            db.close()
