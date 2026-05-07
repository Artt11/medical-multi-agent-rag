from pydantic import BaseModel, Field
from typing import Optional, Literal, Any, Dict

AgentChoices = Literal[
    "medical_retriever_agent",
    "statistical_filter_agent",
    "summarizer_agent",
    "email_reminder_agent",
    "comparative_agent"
]


class AttachmentInfo(BaseModel):
    local_path: str = Field(...,
                            description="Temporary file path on the server")
    file_name: str = Field(..., description="Original file name or blob name")
    content_type: str = "application/pdf"


class RouteDecision(BaseModel):
    target_agent: AgentChoices = Field(
        ..., description="The selected specialized agent for the task")
    extracted_patient_id: Optional[str] = Field(
        None, description="Extracted numeric patient ID or SSN. NEVER extract human names here.")
    extracted_timeframe: Optional[str] = Field(
        None, description="Time period filter (e.g., '2023')")
    extracted_disease: Optional[str] = Field(
        None, description="Specific medical condition")
    needs_pdf: bool = Field(
        False, description="True if the user requests the source PDF")

    english_translation: str = Field(
        ..., description="The exact English translation of the user's medical query. Critical for database searching.")
    detected_language: str = Field(
        ..., description="The language of the user's original query (e.g., 'Armenian', 'Russian', 'English').")


class MedicalSearchQuery(BaseModel):
    query_text: str
    patient_id: Optional[str] = None
    top_k: int = 5


class RetrieverOutput(BaseModel):
    content: str
    page_number: Optional[int] = None
    blob_url: Optional[str] = None
    patient_id: Optional[str] = None
    document_hash: Optional[str] = None
    score: float
    metadata: Dict[str, Any] = {}


class SqlQueryOutput(BaseModel):
    generated_sql: str = Field(..., description="Clean T-SQL query string")
    reasoning: str = Field(...,
                           description="Step-by-step logic for generating the query")
