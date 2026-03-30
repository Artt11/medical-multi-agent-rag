from pydantic import BaseModel, Field
from typing import Optional


class EmailSchema(BaseModel):
    recipient: str = Field(..., description="The target email address")
    subject: str = Field(..., description="Professional email subject")
    body: str = Field(..., description="The professional email body text")
    patient_name: Optional[str] = Field(
        None, description="Patient name if present")
    patient_id: Optional[str] = Field(
        None, description="Patient ID if present")
