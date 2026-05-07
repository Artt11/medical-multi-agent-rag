from typing import Dict, Any
from src.core.config import llm
from src.database.connection import SessionLocal
from src.core.base_email import EmailSchema
from src.services.email_service import (
    send_smtp_email,
    extract_email,
    find_patient_email
)
from src.utils.logger import get_logger
from src.agents.state import AgentState

logger = get_logger("EMAIL_AGENT")


def email_reminder_node(state: AgentState) -> Dict[str, Any]:
    logger.info(
        f"Initiated EMAIL REMINDER AGENT for query: '{state.get('query', '')}'")

    db = SessionLocal()
    patient_id = state.get("patient_id")
    query = state.get("query", "")

    user_lang = state.get("user_language", "Armenian")

    db_email = None
    send_status = "Not Sent"

    try:
        if patient_id:
            logger.debug(
                f"Searching database for email associated with patient ID: {patient_id}")
            db_email, _ = find_patient_email(db, patient_id=patient_id)
            if db_email:
                logger.info(
                    f"Successfully retrieved email from database: {db_email}")

        logger.debug("Invoking LLM for structured email drafting.")
        structured_llm = llm.with_structured_output(EmailSchema)

        system_prompt = f"""
ROLE:
You are an Expert Medical Communications Administrator for a top-tier clinic.
Your task is to draft a highly professional, empathetic, and clear medical reminder email based on the user's request.

<context>
Database Email: {db_email if db_email else "Not found in DB"}
User Request: {query}
</context>

<rules>
1. EMAIL RESOLUTION: Use the Database Email. If missing, extract from User Request. If neither exists, output 'NONE'.
2. LANGUAGE: The email Subject and Body MUST be written in fluent, polite {user_lang}.
</rules>

<email_guidelines>
- TONE: Empathetic, professional, reassuring, and strictly clinical.
- BODY STRUCTURE:
  1. Polite Greeting (e.g., "Dear Patient" or use their name).
  2. The core reminder (date, time, or required action).
  3. Contact info / Call to Action.
  4. Professional Sign-off (e.g., "Best regards, Clinic Administration").
</email_guidelines>
"""
        res = structured_llm.invoke([
            ("system", system_prompt),
            ("human", f"Draft the email for this request: {query}")
        ])

        candidate_id = patient_id or res.patient_id
        db_email, db_error = find_patient_email(
            db, candidate_id, res.patient_name)

        if db_error == "MULTIPLE_MATCHES":
            logger.warning("Multiple patients matched. Aborting.")
            return {
                "final_answer": "⚠️ **Attention:** The system found multiple patients with these details. The email was not sent. Please provide the exact Patient ID or SSN.",
                "email_status": "Failed (Multiple Matches)",
                "next_node": "end"
            }

        recipient = db_email or (
            res.recipient if res.recipient != "NONE" else None) or extract_email(query)

        if recipient and "@" in recipient:
            logger.info(f"Preparing to send SMTP email to: {recipient}")
            send_status = send_smtp_email(recipient, res.subject, res.body)

            final_answer = f"""### 📧 Email Sent Successfully!

**Recipient:** `{recipient}`
**Status:** ✅ {send_status}
**Subject:** {res.subject}

**Message Body:**
> {res.body.replace(chr(10), chr(10) + '> ')} 
"""
        else:
            logger.warning("No valid recipient email address.")
            send_status = "Not Sent (Missing Email Address)"
            final_answer = f"""### ❌ Email Not Sent

**Reason:** The email address was not found in the database or the text.

**Suggested Draft:**
**Subject:** {res.subject}

> {res.body.replace(chr(10), chr(10) + '> ')}
"""

    except Exception as e:
        logger.error(f"Critical execution error: {e}")
        send_status = f"Error: {str(e)}"
        final_answer = f"### ⚠️ System Error\nFailed to process the email request: `{str(e)}`"
    finally:
        db.close()

    return {
        "final_answer": final_answer,
        "email_status": send_status,
        "next_node": "end",
        "intermediate_steps": [f"📧 Էլ. փոստի ագենտը ձևավորեց նամակը և կարգավիճակը թարմացրեց՝ {send_status}:"]
    }
