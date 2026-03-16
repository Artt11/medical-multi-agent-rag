from typing import List, Optional, Any, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr


class MedicalChunk(BaseModel):
    page_content: str = Field(...,
                              description="Chunk-ի բուն տեքստային պարունակությունը")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Լրացուցիչ տվյալներ (source, page, section, patient_id)")


class PatientInfo(BaseModel):
    name: str = Field(default="Unknown")
    dob: Optional[date] = None
    gender: Optional[str] = None
    patient_id: Optional[str] = None
    social_card: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    exam_date: Optional[date] = None
    referring_physician: Optional[str] = None
    # laboratory: Optional[str] = None
    # hospital: Optional[str] = None
    examination_type: Optional[str] = None

    model_config = ConfigDict(extra='ignore')

    @field_validator('dob', 'exam_date', mode='before')
    @classmethod
    def parse_dates(cls, v: Any) -> Optional[date]:
        if not v:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            v = v.strip()
            for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
        return None


class MedicalDocument(BaseModel):
    source: str
    ingested_at: datetime = Field(default_factory=datetime.now)
    patient: PatientInfo = Field(default_factory=PatientInfo)

    measurements: Dict[str, Any] = Field(default_factory=dict)
    diagnosis: List[str] = []
    conclusion: List[str] = []
    recommendations: List[str] = []

    all_data: str = Field(
        default="", description="PDF-ի ամբողջական, չմշակված տեքստը")
    chunks: List[MedicalChunk] = []
    raw_elements: List[Any] = []
    hash: Optional[str] = None
