from pydantic import BaseModel, Field
from typing import Optional, Literal, Any, Dict

AgentChoices = Literal[
    "summarizer_agent",
    "disease_cohort_agent",
    "temporal_disease_agent",
    "email_reminder_agent",
    "comparative_agent",
    "statistical_filter_agent"
]


class AttachmentInfo(BaseModel):
    local_path: str = Field(...,
                            description="Ֆայլի ժամանակավոր հասցեն սերվերի վրա")
    file_name: str = Field(...,
                           description="Ֆայլի օրիգինալ անունը (blob name)")
    content_type: str = "application/pdf"


class RouteDecision(BaseModel):
    target_agent: AgentChoices = Field(...,
                                       description="Ընտրված հատուկ ագենտը")
    extracted_patient_id: Optional[str] = Field(
        None, description="Պացիենտի ID-ն")
    extracted_timeframe: Optional[str] = Field(
        None, description="Ժամանակահատվածը")
    extracted_disease: Optional[str] = Field(
        None, description="Հիվանդությունը")

    needs_pdf: bool = Field(
        False, description="Ճշմարիտ է, եթե օգտատերը հարցնում է անալիզի կամ PDF-ի մասին")


class MedicalSearchQuery(BaseModel):
    query_text: str
    patient_id: Optional[str] = None
    top_k: int = 5


class RetrieverOutput(BaseModel):
    content: str
    page_number: Optional[int] = None
    blob_url: Optional[str] = None
    document_hash: Optional[str] = None
    score: float
    metadata: Dict[str, Any] = {}


class SqlQueryOutput(BaseModel):
    generated_sql: str = Field(..., description="Մաքուր T-SQL հարցումը")
    reasoning: str = Field(..., description="Տրամաբանությունը")
