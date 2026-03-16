# from typing import Dict, Any
# from src.core.config import llm


# def auto_notifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("--- 🔔 AUTO NOTIFIER AGENT (Agent 8) ---")

#     system_prompt = (
#         "You are a Clinical Automated Alert Manager. Your responsibility is to process "
#         "requests for setting up automated medical notifications, background alerts, "
#         "or recurring patient monitoring tasks.\n\n"
#         "Guidelines:\n"
#         "1. Extract the specific conditions for the alert (e.g., laboratory thresholds, timeframes, or disease triggers).\n"
#         "2. Identify the target of the notification (e.g., specific patient ID, medical staff, or a cohort).\n"
#         "3. Output a structured confirmation detailing the active alert configuration.\n"
#         "4. Do not execute the alert immediately; only confirm its configuration for the system's background worker.\n"
#         "5. Maintain strict medical data privacy and a formal clinical tone."
#     )

#     human_message = f"Configure automated alert based on this request: {state['query']}"

#     response = llm.invoke([
#         ("system", system_prompt),
#         ("human", human_message)
#     ])

#     return {
#         "final_answer": response.content,
#         "email_status": "Alert Configured"
#     }
from typing import Dict, Any
from src.core.config import llm


def auto_notifier_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- 🔔 AUTO NOTIFIER AGENT (Agent 8) ---")

    system_prompt = """
ROLE
You are a Clinical Alert Configuration Agent responsible for setting up
automated medical notification rules for the healthcare system.

Your job is NOT to trigger alerts, but to confirm the configuration
of automated monitoring rules that will later be executed by
background system workers.

--------------------------------------------------

TASK

Analyze the user's request and extract the configuration details
for a medical alert or automated notification.

These alerts may involve:

• laboratory value thresholds
• disease triggers
• monitoring timeframes
• patient-specific monitoring
• cohort-based alerts

--------------------------------------------------

REQUIRED EXTRACTION

Identify and clearly specify:

1. Alert Condition
   The clinical event or rule that should trigger the alert.

2. Monitoring Target
   Who or what is being monitored:
   • specific patient ID
   • clinical cohort
   • healthcare staff notification

3. Trigger Criteria
   The exact condition that activates the alert
   (e.g., lab value threshold, diagnosis detection, date interval).

4. Notification Recipient
   Who should receive the alert.

--------------------------------------------------

STRICT RULES

1. CONFIGURATION ONLY
Do NOT trigger alerts or simulate execution.

2. NO MEDICAL INTERPRETATION
Do not diagnose or interpret medical conditions.

3. PRIVACY PROTECTION
Do not expose sensitive patient details unless explicitly provided.

4. MISSING DATA HANDLING
If the request lacks required details, use placeholders such as:

[Patient ID]
[Condition]
[Threshold Value]
[Monitoring Interval]

--------------------------------------------------

OUTPUT FORMAT

Automated Alert Configuration

Alert Type:
<type of monitoring>

Monitoring Target:
<patient / cohort / staff>

Trigger Condition:
<event that activates alert>

Monitoring Timeframe:
<interval or schedule>

Notification Recipient:
<recipient>

Status:
Alert configuration registered for background monitoring.
"""

    human_message = f"Configure automated alert based on this request: {state['query']}"

    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    return {
        "final_answer": response.content,
        "email_status": "Alert Configured"
    }
