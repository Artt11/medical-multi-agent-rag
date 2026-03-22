from typing import Dict, Any, Optional, Tuple
import re
from pydantic import BaseModel, Field
from src.core.config import llm
from src.database.connection import SessionLocal
from src.database.models import PatientModel
from src.services.email_service import send_smtp_email
from sqlalchemy import func


class EmailSchema(BaseModel):
    recipient: str = Field(..., description="The target email address")
    subject: str = Field(..., description="Professional email subject")
    body: str = Field(..., description="The professional email body text")
    patient_name: Optional[str] = Field(
        None, description="Patient name if present")
    patient_id: Optional[str] = Field(
        None, description="Patient ID if present")


EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _extract_email(text: str) -> Optional[str]:
    if not text:
        return None
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def _find_patient_email(
    db: SessionLocal,
    patient_id: Optional[str],
    patient_name: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    if patient_id:
        patient = db.query(PatientModel).filter(
            (PatientModel.patient_id == patient_id)
            | (PatientModel.social_card == patient_id)
        ).first()
        if patient and patient.email:
            return patient.email, None

    if patient_name:
        name_value = patient_name.strip()
        if name_value:
            matches = db.query(PatientModel).filter(
                func.lower(PatientModel.name).like(f"%{name_value.lower()}%")
            ).all()
            if len(matches) > 1:
                return None, "MULTIPLE_MATCHES"
            if len(matches) == 1:
                return matches[0].email, None

    return None, None


def email_reminder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- EMAIL REMINDER AGENT (Agent 4) ---")

    db = SessionLocal()

    patient_id = state.get("patient_id")
    query = state.get("query", "")

    db_email = None
    patient_name = None

    try:
        if patient_id:
            db_email, _ = _find_patient_email(db, patient_id, None)

        structured_llm = llm.with_structured_output(EmailSchema)

        system_prompt = f"""
        You are a Medical Communication Assistant.
        Draft a clinical reminder based on the user request.
        
        CONTEXT:
        - Database Email: {db_email if db_email else "Not found in DB"}
        
        INSTRUCTIONS:
        - Priority 1: Use the Database Email.
        - Priority 2: If DB email is missing, extract from query.
        - If no email found at all, use 'NONE'.
        - Extract patient_name + DOB and patient_id if present.
        """

        res = structured_llm.invoke([
            ("system", system_prompt),
            ("human", f"Request: {query}")
        ])

        patient_name = res.patient_name
        candidate_id = patient_id or res.patient_id

        db_email, db_error = _find_patient_email(
            db, candidate_id, patient_name)

        if db_error == "MULTIPLE_MATCHES":
            send_status = "Չուղարկվեց (մի քանի պացիենտ են համապատասխանում անունին)"
            final_answer = "Խնդրում ենք նշել ավելի կոնկրետ տվյալ (օր. ծննդյան տարեթիվ կամ ID):"
            return {
                "final_answer": final_answer,
                "email_status": send_status
            }

        recipient = db_email or (
            res.recipient if res.recipient != "NONE" else None)
        if not recipient:
            recipient = _extract_email(query)

        if recipient and "@" in recipient:
            send_status = send_smtp_email(recipient, res.subject, res.body)
        else:
            send_status = "Չուղարկվեց (Էլ. հասցեն բացակայում է)"

        final_answer = f"**Կարգավիճակ:** {send_status}\n\n**Նամակ:**\n{res.body}"

    except Exception as e:
        send_status = f"Error: {str(e)}"
        final_answer = f"Տեղի է ունեցել սխալ նամակի մշակման ժամանակ: {str(e)}"
    finally:
        db.close()

    return {
        "final_answer": final_answer,
        "email_status": send_status
    }
