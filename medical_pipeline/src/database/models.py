from sqlalchemy import Column, Integer, Date, ForeignKey, String, JSON
from src.database.connection import Base


class PatientModel(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    dob = Column(Date)
    gender = Column(String(50))
    email = Column(String(255))
    phone = Column(String(50))
    social_card = Column(String(100), unique=True, index=True)
    patient_id = Column(String(100), unique=True,
                        index=True)


class MedicalExamModel(Base):
    __tablename__ = "medical_exams"

    exam_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))

    source_file = Column(String(255))
    exam_date = Column(Date)
    examination_type = Column(String(255))
    referring_physician = Column(String(255))

    diagnosis = Column(JSON)
    conclusion = Column(JSON)
    recommendations = Column(JSON)
    full_json = Column(JSON)

    document_hash = Column(String(64), unique=True, index=True)
