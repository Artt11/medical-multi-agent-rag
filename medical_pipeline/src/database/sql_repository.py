from sqlalchemy.orm import Session
from typing import Iterable
from src.core.base_repository import IDatabaseRepository
from src.models.document import MedicalDocument
from src.database.models import PatientModel, MedicalExamModel
from src.utils.logger import get_logger

logger = get_logger("DATABASE")


class SqlDatabaseRepository(IDatabaseRepository):
    def __init__(self, db: Session):
        logger.debug("Attempting to connect via SQL Session")
        self.db = db

    def save(self, document: MedicalDocument, source_url: str = "") -> None:
        try:
            existing_exam = self.db.query(MedicalExamModel).filter(
                MedicalExamModel.document_hash == document.hash
            ).first()

            if existing_exam:
                logger.info(
                    f"Ֆայլը արդեն գոյություն ունի (Hash: {document.hash})։ Բաց ենք թողնում:")
                return

            patient = self._get_or_create_patient(document.patient)

            self._save_exam_metadata(patient.id, document, source_url)

            self.db.commit()
            logger.info(
                f"SQL Saved. Հաջողությամբ պահպանվեց բազայում: Պացիենտ՝ {patient.name}")
        except Exception as e:
            self.db.rollback()
            if "pyodbc.OperationalError" in str(type(e)) or "operationalerror" in str(e).lower() or "timeout" in str(e).lower() or "interfaceerror" in str(e).lower():
                logger.critical(
                    "🚨 DATABASE TIMEOUT: Check Azure Firewall and IP whitelist.")
            else:
                logger.error(f"SQL Save Error: {e}")
            raise

    def list(self) -> Iterable[MedicalExamModel]:
        return self.db.query(MedicalExamModel).all()

    def _get_or_create_patient(self, patient_data):

        existing = None

        if patient_data.social_card:
            existing = self.db.query(PatientModel).filter(
                PatientModel.social_card == patient_data.social_card
            ).first()

        if not existing:
            existing = self.db.query(PatientModel).filter(
                PatientModel.name == patient_data.name,
                PatientModel.dob == patient_data.dob
            ).first()

        if existing:
            return existing

        new_patient = PatientModel(
            name=patient_data.name,
            social_card=patient_data.social_card,
            dob=patient_data.dob,
            gender=patient_data.gender,
            email=patient_data.email,
            phone=patient_data.phone,
            patient_id=patient_data.social_card or patient_data.patient_id
        )
        self.db.add(new_patient)
        self.db.flush()
        return new_patient

    def _save_exam_metadata(self, patient_internal_id: int, doc: MedicalDocument, source_url: str):

        exam = MedicalExamModel(
            patient_id=patient_internal_id,
            source_file=doc.source,
            source_url=source_url,
            document_hash=doc.hash,
            exam_date=doc.patient.exam_date,
            examination_type=doc.patient.examination_type,
            referring_physician=doc.patient.referring_physician,
            diagnosis=doc.diagnosis,
            conclusion=doc.conclusion,
            recommendations=doc.recommendations,
            full_json=doc.model_dump(mode='json')
        )
        self.db.add(exam)
