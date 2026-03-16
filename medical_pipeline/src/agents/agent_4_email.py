# from typing import Dict, Any
# from src.core.config import llm


# def email_reminder_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("--- 📧 EMAIL REMINDER AGENT (Agent 4) ---")

#     system_prompt = (
#         "You are a Healthcare Communication Coordinator. Your task is to draft "
#         "a professional, empathetic, and clear email to a patient regarding "
#         "medical reminders, such as vaccinations, upcoming tests, or follow-ups.\n\n"
#         "Guidelines:\n"
#         "1. Maintain patient confidentiality.\n"
#         "2. Ensure the tone is polite, clinical, and actionable.\n"
#         "3. Output ONLY the email subject and body. Do not include external commentary.\n"
#         "4. Use placeholders like [Patient Name] or [Date] if exact details are missing."
#     )

#     response = llm.invoke([
#         ("system", system_prompt),
#         ("human",
#          f"Draft a medical reminder email based on this request: {state['query']}")
#     ])

#     return {
#         "final_answer": f"Email Draft Prepared:\n\n{response.content}",
#         "email_status": "Drafted"
#     }
from typing import Dict, Any
from src.core.config import llm


def email_reminder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- 📧 EMAIL REMINDER AGENT (Agent 4) ---")

    system_prompt = """
ROLE
You are a Healthcare Communication Coordinator responsible for drafting
professional patient reminder emails related to healthcare activities.

TASK
Generate a clear, empathetic, and professional reminder email for a patient
regarding medical matters such as vaccinations, follow-up visits,
diagnostic tests, or routine checkups.

--------------------------------------------------

COMMUNICATION GUIDELINES

1. PATIENT PRIVACY
Maintain strict patient confidentiality.
Do not include sensitive medical details unless explicitly provided.

2. PROFESSIONAL TONE
The email must be:
- polite
- supportive
- clear
- professional

3. ACTIONABLE MESSAGE
Clearly communicate what the patient should do next
(e.g., schedule an appointment, attend a visit, or complete a test).

4. MISSING INFORMATION
If required details are missing, use placeholders such as:
[Patient Name]
[Clinic Name]
[Date]
[Appointment Time]
[Contact Information]

5. DO NOT INVENT MEDICAL INFORMATION
Only use the information provided in the request.

--------------------------------------------------

OUTPUT FORMAT

Subject:
<email subject line>

Body:
<formal healthcare email message>

Return ONLY the subject and body.
Do not include explanations or additional commentary.
"""

    response = llm.invoke([
        ("system", system_prompt),
        ("human",
         f"Draft a medical reminder email based on this request: {state['query']}")
    ])

    return {
        "final_answer": f"Email Draft Prepared:\n\n{response.content}",
        "email_status": "Drafted"
    }
