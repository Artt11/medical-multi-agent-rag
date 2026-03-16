# from sqlalchemy.orm import Session
# from typing import Iterable
# from src.core.base_repository import IDatabaseRepository
# from src.models.document import MedicalDocument
# from src.database.models import PatientModel, MedicalExamModel


# class SqlDatabaseRepository(IDatabaseRepository):
#     def __init__(self, db: Session):

#         self.db = db

#     def save(self, document: MedicalDocument) -> None:

#         patient = self._get_or_create_patient(document.patient)

#         self._save_exam_metadata(patient.id, document)

#         self.db.commit()

#     def list(self) -> Iterable[MedicalDocument]:

#         return self.db.query(MedicalExamModel).all()

#     def _get_or_create_patient(self, patient_data):
#         if patient_data.social_card:
#             existing = self.db.query(PatientModel).filter(
#                 PatientModel.social_card == patient_data.social_card
#             ).first()
#             if existing:
#                 return existing

#         new_patient = PatientModel(
#             name=patient_data.name,
#             social_card=patient_data.social_card,
#             dob=patient_data.dob,
#             gender=patient_data.gender,
#             email=patient_data.email,
#             phone=patient_data.phone,
#             patient_id=patient_data.patient_id
#         )
#         self.db.add(new_patient)
#         self.db.flush()
#         return new_patient

#     def _save_exam_metadata(self, patient_internal_id: int, doc: MedicalDocument):
#         exam = MedicalExamModel(
#             patient_id=patient_internal_id,
#             source_file=doc.source,
#             document_hash=doc.hash,
#             exam_date=doc.patient.exam_date,
#             examination_type=doc.patient.examination_type,
#             referring_physician=doc.patient.referring_physician,
#             diagnosis=doc.diagnosis,
#             conclusion=doc.conclusion,
#             recommendations=doc.recommendations,
#             full_json=doc.model_dump(mode='json')
#         )
#         self.db.add(exam)
from sqlalchemy.orm import Session
from typing import Iterable
from src.core.base_repository import IDatabaseRepository
from src.models.document import MedicalDocument
from src.database.models import PatientModel, MedicalExamModel


class SqlDatabaseRepository(IDatabaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, document: MedicalDocument) -> None:

        existing_exam = self.db.query(MedicalExamModel).filter(
            MedicalExamModel.document_hash == document.hash
        ).first()

        if existing_exam:
            print(
                f"⚠️ Ֆայլը արդեն գոյություն ունի (Hash: {document.hash})։ Բաց ենք թողնում:")
            return

        # 2. ՊԱՑԻԵՆՏԻ ՍՏՈՒԳՈՒՄ (Get or Create)
        # Գտնում ենք հին պացիենտին կամ ստեղծում նորին
        patient = self._get_or_create_patient(document.patient)

        # 3. ԱՆԱԼԻԶԻ ՊԱՀՊԱՆՈՒՄ
        # Ստեղծում ենք նոր տող medical_exams-ում և կապում պացիենտի ID-ի հետ
        self._save_exam_metadata(patient.id, document)

        # 4. ՎԵՐՋՆԱԿԱՆ ՀԱՍՏԱՏՈՒՄ
        self.db.commit()
        print(f"✅ Հաջողությամբ պահպանվեց բազայում: Պացիենտ՝ {patient.name}")

    def list(self) -> Iterable[MedicalDocument]:
        return self.db.query(MedicalExamModel).all()

    def _get_or_create_patient(self, patient_data):
        """
        Փնտրում է պացիենտին բազայում: Եթե չկա, ստեղծում է նորը:
        """
        existing = None

        # Ա. Փնտրում ենք ըստ Social Card-ի
        if patient_data.social_card:
            existing = self.db.query(PatientModel).filter(
                PatientModel.social_card == patient_data.social_card
            ).first()

        # Բ. Եթե չկա, փնտրում ենք ըստ Անվան և Ծննդյան օրվա (SQL Unique Constraint-ի համար)
        if not existing:
            existing = self.db.query(PatientModel).filter(
                PatientModel.name == patient_data.name,
                PatientModel.dob == patient_data.dob
            ).first()

        # Գ. Եթե գտանք, վերադարձնում ենք գոյություն ունեցողին
        if existing:
            return existing

        # Դ. Եթե չգտանք, ստեղծում ենք նոր պացիենտ
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
        self.db.flush()  # Ստանում ենք ID-ն հաջորդ քայլի համար
        return new_patient

    def _save_exam_metadata(self, patient_internal_id: int, doc: MedicalDocument):

        exam = MedicalExamModel(
            patient_id=patient_internal_id,
            source_file=doc.source,
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
