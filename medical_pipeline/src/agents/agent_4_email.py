from typing import Dict, Any
from src.core.config import llm
from src.database.connection import SessionLocal
from src.core.base_email import EmailSchema
from src.services.email_service import (
    send_smtp_email,
    extract_email,
    find_patient_email
)


def email_reminder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- EMAIL REMINDER AGENT (Agent 4) ---")

    db = SessionLocal()
    patient_id = state.get("patient_id")
    query = state.get("query", "")

    db_email = None
    send_status = "Չուղարկվեց"

    try:
        if patient_id:
            db_email, _ = find_patient_email(db, patient_id=patient_id)

        structured_llm = llm.with_structured_output(EmailSchema)

        system_prompt = f"""
        You are a Medical Communication Assistant.
        Draft a clinical reminder based on the user request.
        
        CONTEXT:
        - Database Email: {db_email if db_email else "Not found in DB"}
        
        INSTRUCTIONS:
        - Priority 1: Use the Database Email.
        - Priority 2: If DB email is missing, extract from query or context.
        - If no email found at all, use 'NONE'.
        - Extract patient_name and patient_id if present in the text.
        """

        res = structured_llm.invoke([
            ("system", system_prompt),
            ("human", f"Request: {query}")
        ])

        candidate_id = patient_id or res.patient_id
        db_email, db_error = find_patient_email(
            db, candidate_id, res.patient_name)

        if db_error == "MULTIPLE_MATCHES":
            return {
                "final_answer": "Համակարգը գտել է մի քանի պացիենտ նույն տվյալներով։ Խնդրում ենք նշել ՀԾՀ-ն:",
                "email_status": "Չուղարկվեց (Multiple Matches)"
            }

        recipient = db_email
        if not recipient:
            recipient = res.recipient if res.recipient != "NONE" else None
        if not recipient:
            recipient = extract_email(query)

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
