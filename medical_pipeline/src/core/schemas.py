# from pydantic import BaseModel, Field
# from typing import Optional, Dict, Any


# class MedicalSearchQuery(BaseModel):
#     query_text: str = Field(..., description="Հարցի բովանդակությունը")
#     patient_id: str = Field(..., description="Պացիենտի ID-ն ֆիլտրման համար")
#     top_k: int = Field(default=5, ge=1, le=20)


# class RetrieverOutput(BaseModel):
#     content: str = Field(..., description="Chunk-ի բուն տեքստը")
#     page_number: Optional[int] = Field(None)
#     blob_url: str = Field(..., description="Հղումը դեպի PDF")
#     score: float = Field(..., description="Ճշգրտության միավորը (RRF/Semantic)")
#     metadata: Dict[str, Any] = Field(default_factory=dict)


# class RouteDecision(BaseModel):
#     target_agent: str = Field(
#         ..., description="Ագենտի անունը (sql_stats_agent կամ advanced_rag_agent)")
#     extracted_patient_id: Optional[str] = Field(
#         None, description="Հարցից արտահանված պացիենտի ID-ն")

from pydantic import BaseModel, Field
from typing import Optional, Literal, Any, Dict

# 1. Օրկեստրատորի համար (Routing)
AgentChoices = Literal[
    "summarizer_agent",
    "disease_cohort_agent",
    "temporal_disease_agent",
    "email_reminder_agent",
    "comparative_agent",
    "source_retriever_agent",
    "statistical_filter_agent",
    "auto_notifier_agent"
]


class RouteDecision(BaseModel):
    target_agent: AgentChoices = Field(...,
                                       description="Ընտրված հատուկ ագենտը")
    extracted_patient_id: Optional[str] = Field(
        None, description="Պացիենտի ID-ն")
    extracted_timeframe: Optional[str] = Field(
        None, description="Ժամանակահատվածը")
    extracted_disease: Optional[str] = Field(
        None, description="Հիվանդությունը")

# 2. Որոնման համար (Retriever) - ՍԱ ԷՐ ՊԱԿԱՍՈՒՄ


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

# 3. SQL Ագենտների համար (Structured Output)


class SqlQueryOutput(BaseModel):
    generated_sql: str = Field(..., description="Մաքուր T-SQL հարցումը")
    reasoning: str = Field(..., description="Տրամաբանությունը")
