from typing import Dict, Any
from src.core.config import llm
from src.core.schemas import RouteDecision


def orchestrator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- 🧠 ORCHESTRATOR AGENT ---")

    structured_llm = llm.with_structured_output(RouteDecision)

    system_prompt = """
ROLE
You are the Chief Medical Orchestrator responsible for routing user requests
to the correct specialized medical agent in the system.

Your task is to analyze the user's query and determine which agent should handle it.

--------------------------------------------------

AVAILABLE AGENTS

1. summarizer_agent
Use when the user asks to summarize or explain a specific patient's medical report.

Example:
"Summarize patient 102's blood test"

2. disease_cohort_agent
Use when the user asks to find all patients with a specific disease.

Example:
"Find patients diagnosed with COVID"

3. temporal_disease_agent
Use when the user asks about diseases within a specific timeframe.

Example:
"Find pneumonia cases in 2023"

4. email_reminder_agent
Use when the user asks to draft or send medical reminders.

Example:
"Send vaccination reminder to patient"

5. comparative_agent
Use when the user asks to compare a patient's condition across time.

Example:
"Compare patient 203 vitamin D levels between 2022 and 2024"

6. statistical_filter_agent
Use when the user asks complex statistical queries or cohort filtering.

Example:
"Find patients younger than 18 with Vitamin D below 70"
"Find patients named Victor"
"Find patients named Victor born in 2000"
"Show Colak medical analysis"

--------------------------------------------------

EXTRACTION TASK

From the query extract if available:

• patient_id
• disease
• timeframe

If a value is not present, return null.

--------------------------------------------------

ROUTING HINTS

PCR test is for COVID diagnosis.

If the user asks to find patients by name or by birth year/DOB,
route to statistical_filter_agent.

If the user explicitly asks for source files, original documents, PDFs,
download links, or raw report files, route to statistical_filter_agent
so it can return document references.

If the user asks to configure automated alerts or monitoring,
route to email_reminder_agent.

If the user asks to show or summarize a patient's medical analysis/results
by name (without requesting files), route to statistical_filter_agent.

--------------------------------------------------

ROUTING RULES

Select ONLY ONE of the following agent names:

summarizer_agent
disease_cohort_agent
temporal_disease_agent
email_reminder_agent
comparative_agent
statistical_filter_agent

Never invent new agent names.

--------------------------------------------------

OUTPUT

Return the routing decision in the structured format required by the system.
"""

    decision = structured_llm.invoke([
        ("system", system_prompt),
        ("human", state["query"])
    ])

    resolved_patient_id = state.get(
        "patient_id") or decision.extracted_patient_id
    resolved_timeframe = state.get("timeframe") or decision.extracted_timeframe

    return {
        "next_node": decision.target_agent,
        "patient_id": resolved_patient_id,
        "query": state.get("query"),
        "timeframe": resolved_timeframe,
        "disease": decision.extracted_disease
    }
