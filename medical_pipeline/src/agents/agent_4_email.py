# from typing import Dict, Any
# from src.core.config import llm
# from src.database.connection import SessionLocal
# from src.core.base_email import EmailSchema
# from src.services.email_service import (
#     send_smtp_email,
#     extract_email,
#     find_patient_email
# )


# def email_reminder_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("--- EMAIL REMINDER AGENT (Agent 4) ---")

#     db = SessionLocal()
#     patient_id = state.get("patient_id")
#     query = state.get("query", "")

#     db_email = None
#     send_status = "Չուղարկվեց"

#     try:
#         if patient_id:
#             db_email, _ = find_patient_email(db, patient_id=patient_id)

#         structured_llm = llm.with_structured_output(EmailSchema)

#         system_prompt = f"""
#         You are a Medical Communication Assistant.
#         Draft a clinical reminder based on the user request.

#         CONTEXT:
#         - Database Email: {db_email if db_email else "Not found in DB"}

#         INSTRUCTIONS:
#         - Priority 1: Use the Database Email.
#         - Priority 2: If DB email is missing, extract from query or context.
#         - If no email found at all, use 'NONE'.
#         - Extract patient_name and patient_id if present in the text.
#         """

#         res = structured_llm.invoke([
#             ("system", system_prompt),
#             ("human", f"Request: {query}")
#         ])

#         candidate_id = patient_id or res.patient_id
#         db_email, db_error = find_patient_email(
#             db, candidate_id, res.patient_name)

#         if db_error == "MULTIPLE_MATCHES":
#             return {
#                 "final_answer": "Համակարգը գտել է մի քանի պացիենտ նույն տվյալներով։ Խնդրում ենք նշել ՀԾՀ-ն:",
#                 "email_status": "Չուղարկվեց (Multiple Matches)"
#             }

#         recipient = db_email
#         if not recipient:
#             recipient = res.recipient if res.recipient != "NONE" else None
#         if not recipient:
#             recipient = extract_email(query)

#         if recipient and "@" in recipient:
#             send_status = send_smtp_email(recipient, res.subject, res.body)
#         else:
#             send_status = "Չուղարկվեց (Էլ. հասցեն բացակայում է)"

#         final_answer = f"**Կարգավիճակ:** {send_status}\n\n**Նամակ:**\n{res.body}"

#     except Exception as e:
#         send_status = f"Error: {str(e)}"
#         final_answer = f"Տեղի է ունեցել սխալ նամակի մշակման ժամանակ: {str(e)}"
#     finally:
#         db.close()

#     return {
#         "final_answer": final_answer,
#         "email_status": send_status
#     }
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
    print("--- 📧 EMAIL REMINDER AGENT (Agent 4 - Optimized) ---")

    db = SessionLocal()
    patient_id = state.get("patient_id")
    query = state.get("query", "")

    db_email = None
    send_status = "Չուղարկվեց"

    try:
        # Նախնական որոնում բազայում, եթե ID-ն կա
        if patient_id:
            db_email, _ = find_patient_email(db, patient_id=patient_id)

        structured_llm = llm.with_structured_output(EmailSchema)

        # ==========================================
        # 1. OPTIMIZED EMAIL GENERATION PROMPT
        # ==========================================
        system_prompt = f"""
ROLE:
You are an Expert Medical Communications Administrator for a top-tier clinic.
Your task is to draft a highly professional, empathetic, and clear medical reminder email based on the user's request.

<context>
Database Email: {db_email if db_email else "Not found in DB"}
User Request: {query}
</context>

<rules>
1. EMAIL RESOLUTION PRIORITY:
   - Priority 1: Use the Database Email provided above.
   - Priority 2: If DB Email is missing, meticulously extract it from the User Request.
   - Priority 3: If completely missing, output exactly 'NONE' for the recipient field.
2. ENTITY EXTRACTION: Accurately extract `patient_name` and `patient_id` from the text if they are mentioned.
3. LANGUAGE: The email Subject and Body MUST be written in fluent, polite Armenian.
</rules>

<email_guidelines>
- TONE: Empathetic, professional, reassuring, and strictly clinical.
- SUBJECT: Must be clear and urgent but not alarming (e.g., "Հիշեցում Ձեր բժշկական այցի վերաբերյալ").
- BODY STRUCTURE:
  1. Polite Greeting (e.g., "Հարգելի պացիենտ" or use their name).
  2. The core reminder (date, time, or required action).
  3. Contact info / Call to Action (e.g., "Հարցերի դեպքում կապ հաստատեք մեզ հետ").
  4. Professional Sign-off (e.g., "Հարգանքով՝ Կլինիկայի ադմինիստրացիա").
</email_guidelines>
"""

        res = structured_llm.invoke([
            ("system", system_prompt),
            ("human", f"Draft the email for this request: {query}")
        ])

        # Նույնականացնում ենք պացիենտին (ID կամ Անուն)
        candidate_id = patient_id or res.patient_id
        db_email, db_error = find_patient_email(
            db, candidate_id, res.patient_name)

        # Ստուգում ենք Multiple Matches-ի քեյսը
        if db_error == "MULTIPLE_MATCHES":
            return {
                "final_answer": "⚠️ **Ուշադրություն:** Համակարգը գտել է մի քանի պացիենտ նույն տվյալներով։ Նամակը չի ուղարկվել։ Խնդրում ենք նշել պացիենտի ՀԾՀ-ն կամ ID-ն։",
                "email_status": "Չուղարկվեց (Multiple Matches)"
            }

        # Որոշում ենք վերջնական ստացողին (Recipient logic)
        recipient = db_email
        if not recipient:
            recipient = res.recipient if res.recipient != "NONE" else None
        if not recipient:
            recipient = extract_email(query)

        # Ուղարկելու լոգիկա
        if recipient and "@" in recipient:
            send_status = send_smtp_email(recipient, res.subject, res.body)
            # Հաջողության դեպքում սարքում ենք սիրուն արդյունք
            final_answer = f"""### 📧 Նամակն ուղարկված է!

**Ստացող:** `{recipient}`
**Կարգավիճակ:** ✅ {send_status}

**Թեմա:** {res.subject}

**Նամակի բովանդակություն:**
> {res.body.replace(chr(10), chr(10) + '> ')} 
"""
        else:
            send_status = "Չուղարկվեց (Էլ. հասցեն բացակայում է)"
            final_answer = f"""### ❌ Նամակը չի ուղարկվել

**Պատճառ:** Էլ. փոստի հասցեն գտնված չէ բազայում կամ տեքստում։

**Առաջարկվող նամակի տեքստը (Դրաֆտ):**
**Թեմա:** {res.subject}

> {res.body.replace(chr(10), chr(10) + '> ')}
"""

    except Exception as e:
        send_status = f"Error: {str(e)}"
        final_answer = f"### ⚠️ Տեղի է ունեցել համակարգային սխալ\nՆամակի մշակումը ձախողվեց: `{str(e)}`"
    finally:
        db.close()

    return {
        "final_answer": final_answer,
        "email_status": send_status
    }
