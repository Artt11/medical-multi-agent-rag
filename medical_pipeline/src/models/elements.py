from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum


class ElementType(str, Enum):
    TEXT = "text"
    TABLE = "table"


class ParsedElement(BaseModel):
    type: ElementType
    content: Any
    page: Optional[int] = None
    top: float = 0.0


# class EmailSchema(BaseModel):
#     recipient: str = Field(..., description="The target email address")
#     subject: str = Field(..., description="Professional email subject")
#     body: str = Field(..., description="The professional email body text")
#     patient_name: Optional[str] = Field(
#         None, description="Patient name if present")
#     patient_id: Optional[str] = Field(
#         None, description="Patient ID if present")
