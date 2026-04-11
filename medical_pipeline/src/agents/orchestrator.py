# from typing import Dict, Any
# from src.core.config import llm
# from src.core.schemas import RouteDecision


# def orchestrator_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("---ORCHESTRATOR AGENT ---")

#     structured_llm = llm.with_structured_output(RouteDecision)

#     system_prompt = """
# ROLE
# You are the Chief Medical Orchestrator responsible for routing user requests
# to the correct specialized medical agent in the system.

# Your task is to analyze the user's query and determine which agent should handle it.

# --------------------------------------------------

# AVAILABLE AGENTS

# 1. summarizer_agent
# Use when the user asks to summarize or explain a specific patient's medical report.

# Example:
# "Summarize patient 102's blood test"

# 2. disease_cohort_agent
# Use when the user asks to find all patients with a specific disease.

# Example:
# "Find patients diagnosed with COVID"

# 3. temporal_disease_agent
# Use when the user asks about diseases within a specific timeframe.

# Example:
# "Find pneumonia cases in 2023"

# 4. email_reminder_agent
# Use when the user asks to draft or send medical reminders.

# Example:
# "Send vaccination reminder to patient"

# 5. comparative_agent
# Use when the user asks to compare a patient's condition across time.

# Example:
# "Compare patient 203 vitamin D levels between 2022 and 2024"

# 6. statistical_filter_agent
# Use when the user asks complex statistical queries or cohort filtering.

# Example:
# "Find patients younger than 18 with Vitamin D below 70"
# "Find patients named Victor"
# "Find patients named Victor born in 2000"
# "Show Colak medical analysis"

# --------------------------------------------------

# EXTRACTION TASK

# From the query extract if available:

# • patient_id
# • disease
# • timeframe

# If a value is not present, return null.

# --------------------------------------------------

# ROUTING HINTS

# PCR test is for COVID .

# If the user asks to find patients by name or by birth year/DOB,
# route to statistical_filter_agent.

# If the user explicitly asks for source files, original documents, PDFs,
# download links, or raw report files, route to statistical_filter_agent
# so it can return document references.

# If the user asks to configure automated alerts or monitoring,
# route to email_reminder_agent.

# If the user asks to show or summarize a patient's medical analysis/results
# by name (without requesting files), route to statistical_filter_agent.

# --------------------------------------------------

# ROUTING RULES

# Select ONLY ONE of the following agent names:

# summarizer_agent
# disease_cohort_agent
# temporal_disease_agent
# email_reminder_agent
# comparative_agent
# statistical_filter_agent

# Never invent new agent names.

# --------------------------------------------------

# OUTPUT

# Return the routing decision in the structured format required by the system.
# """

#     decision = structured_llm.invoke([
#         ("system", system_prompt),
#         ("human", state["query"])
#     ])

#     resolved_patient_id = state.get(
#         "patient_id") or decision.extracted_patient_id
#     resolved_timeframe = state.get("timeframe") or decision.extracted_timeframe

#     return {
#         "next_node": decision.target_agent,
#         "patient_id": resolved_patient_id,
#         "query": state.get("query"),
#         "timeframe": resolved_timeframe,
#         "disease": decision.extracted_disease
#     }
from typing import Dict, Any
from src.core.config import llm
from src.core.schemas import RouteDecision
from src.utils.logger import get_logger

logger = get_logger("ORCHESTRATOR")

def orchestrator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Incoming query: {state.get('query', '')}")

    structured_llm = llm.with_structured_output(RouteDecision)

    # ==========================================
    # OPTIMIZED ROUTING PROMPT
    # ==========================================
    system_prompt = """
ROLE:
You are the Chief Medical Orchestrator. Your absolute priority is to analyze the user's natural language query, extract key medical entities, and route the request to the EXACT correct specialized agent.

<agent_boundaries>
1. summarizer_agent
   - INTENT: User wants a clinical summary, explanation, or general overview of ONE specific patient's medical records/exams.
   - TRIGGERS: "Summarize patient 102's blood test", "What is the health status of patient X?"
   
2. comparative_agent
   - INTENT: User explicitly asks to COMPARE a patient's metrics, lab results, or condition across MULTIPLE time periods or dates.
   - TRIGGERS: "Compare vitamin D levels of patient 203 between 2022 and 2024", "Has the patient's cholesterol improved since last year?"

3. disease_cohort_agent
   - INTENT: User wants to find a list of patients with a SPECIFIC DISEASE/CONDITION, with NO complex statistical filters or timeframes.
   - TRIGGERS: "Find patients diagnosed with COVID", "Show me patients with hypertension."

4. temporal_disease_agent
   - INTENT: User searches for diseases/conditions restricted by a SPECIFIC TIMEFRAME (year, month, recent days).
   - TRIGGERS: "Find pneumonia cases in 2023", "Who got flu in the last 2 months?"

5. statistical_filter_agent
   - INTENT: User asks for complex queries: demographics (age, gender), exact name searches, metric thresholds (>, <, =), or requesting raw source files/PDFs.
   - TRIGGERS: "Find patients younger than 18 with Vitamin D below 70", "Find patients named Victor born in 2000", "Show Colak's medical analysis", "Give me the source PDF for patient 5."

6. email_reminder_agent
   - INTENT: The core intent is COMMUNICATION (sending emails, drafting reminders, setting up alerts).
   - TRIGGERS: "Send vaccination reminder to patient 10", "Draft an email for upcoming checkups."
</agent_boundaries>

<extraction_rules>
Carefully extract the following if present in the text:
- `patient_id`: Numeric IDs, or exact names if used as an identifier (e.g., Social Card).
- `disease`: Medical conditions (e.g., COVID, Pneumonia, Diabetes). Map symptoms or tests to the core disease internally if obvious.
- `timeframe`: Dates, years, or periods (e.g., "2023", "last 6 months").
If a value is entirely missing, return `null`. Do not guess.
</extraction_rules>

<routing_logic>
- MUTUAL EXCLUSIVITY: Choose ONLY ONE agent from the list above.
- NAME SEARCHES: If searching by a person's exact name (not ID), route to `statistical_filter_agent`.
- DOCUMENT REQUESTS: If explicitly asking for original files/PDFs/links, route to `statistical_filter_agent`.
- PRECISION: Match the CORE intent of the prompt. Do not overcomplicate.
</routing_logic>
"""

    decision = structured_llm.invoke([
        ("system", system_prompt),
        ("human", f"User Query: {state.get('query', '')}")
    ])

    # Պահպանում ենք state-ի արժեքները որպես առաջնահերթություն, եթե դրանք արդեն կան
    resolved_patient_id = state.get(
        "patient_id") or decision.extracted_patient_id
    resolved_timeframe = state.get("timeframe") or decision.extracted_timeframe
    resolved_disease = state.get("disease") or decision.extracted_disease

    logger.warning(
        f"RouteDecision: Target Agent={decision.target_agent}, Extracted Entities: ID={resolved_patient_id}, Time={resolved_timeframe}, Disease={resolved_disease}"
    )

    return {
        "next_node": decision.target_agent,
        "patient_id": resolved_patient_id,
        "query": state.get("query"),
        "timeframe": resolved_timeframe,
        "disease": resolved_disease
    }
