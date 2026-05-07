# from typing import Dict, Any
# from src.core.config import llm
# from src.core.schemas import RouteDecision
# from src.utils.logger import get_logger
# from src.agents.state import AgentState

# logger = get_logger("ORCHESTRATOR")


# def orchestrator_node(state: AgentState) -> Dict[str, Any]:
#     logger.info(
#         f"Initiating orchestration for query: {state.get('query', '')}")

#     structured_llm = llm.with_structured_output(RouteDecision)

#     system_prompt = """

# IDENTITY:
# You are the Chief Medical Intelligence Orchestrator (CMIO).

# AGENT DOMAINS:
# 1. statistical_filter_agent: ANY request asking for a LIST of patients, "ALL patients", counts, demographics, or finding patients by a specific disease/condition.
# 2. medical_retriever_agent: Deep medical analysis of a SINGLE patient's clinical notes/history, or finding very specific unstructured symptoms.
# 3. summarizer_agent: Full medical history summarization for ONE patient.
# 4. comparative_agent: Dynamic trend analysis over different dates for ONE patient.
# 5. email_reminder_agent: Email drafting and clinical communications.

# ROUTING HEURISTICS (CRITICAL!):
# - If the user asks "Show all patients...", "List patients...", "How many...", or "Who has [DISEASE]?" -> ALWAYS route to `statistical_filter_agent`.

# TRANSLATION & QUERY EXPANSION PROTOCOL (CRITICAL!):
# 1. Detect the user's language and store it in `detected_language`.
# 2. MEDICAL EXPANSION: If the user mentions ANY disease, symptom, or medical condition, DO NOT just translate it. You MUST expand it into a comprehensive boolean search string containing the primary term, synonyms, and diagnostic tests (e.g., "Covid" -> "COVID-19 OR SARS-CoV-2 OR PCR positive").
# 3. If the user asks for "ALL patients" without a specific disease, output exactly: "ALL_PATIENTS".
# 4. Store this string in `english_translation`.
# """

#     decision = structured_llm.invoke([
#         ("system", system_prompt),
#         ("human", f"User Query: {state.get('query', '')}")
#     ])

#     resolved_patient_id = state.get(
#         "patient_id") or decision.extracted_patient_id
#     resolved_timeframe = state.get("timeframe") or decision.extracted_timeframe
#     resolved_disease = state.get("disease") or decision.extracted_disease

#     logger.warning(
#         f"Routing: Agent='{decision.target_agent}' | Lang='{decision.detected_language}' | EN_Query='{decision.english_translation}'"
#     )

#     return {
#         "next_node": decision.target_agent,
#         "patient_id": resolved_patient_id,
#         "query": state.get("query"),
#         "english_query": decision.english_translation,
#         "user_language": decision.detected_language,
#         "timeframe": resolved_timeframe,
#         "disease": resolved_disease,
#         "needs_pdf": decision.needs_pdf,
#         "intermediate_steps": [
#             f"🧠 **Օրքեստրատոր**։ Հարցումը վերլուծվեց ({decision.detected_language})։ "
#             f"Որոշվեց դիմել `{decision.target_agent}`-ին։ "
#             f"Անգլերեն հարցում՝ \"{decision.english_translation}\""
#         ]
#     }
from typing import Dict, Any
from src.core.config import llm
from src.core.schemas import RouteDecision
from src.utils.logger import get_logger
from src.agents.state import AgentState

logger = get_logger("ORCHESTRATOR")


def orchestrator_node(state: AgentState) -> Dict[str, Any]:
    logger.info(
        f"Initiating orchestration for query: {state.get('query', '')}")

    structured_llm = llm.with_structured_output(RouteDecision)

    system_prompt = """
IDENTITY:
You are the Chief Medical Intelligence Orchestrator (CMIO). 

AGENT DOMAINS:
1. statistical_filter_agent: ANY request asking for a LIST of patients, "ALL patients", counts, demographics, or finding patients by a specific disease/condition.
2. medical_retriever_agent: Deep medical analysis of a SINGLE patient's clinical notes/history, or finding very specific unstructured symptoms.
3. summarizer_agent: Full medical history summarization for ONE patient.
4. comparative_agent: Dynamic trend analysis over different dates for ONE patient.
5. email_reminder_agent: Email drafting and clinical communications.

ROUTING HEURISTICS (CRITICAL!):
- If the user asks "Show all patients...", "List patients...", "How many...", or "Who has [DISEASE]?" -> ALWAYS route to `statistical_filter_agent`.
- If a query involves a group list AND a specific status (e.g., "Who is negative?"), route to `statistical_filter_agent`.

IDENTITY PRESERVATION & TRANSLITERATION (CRITICAL!):
1. DETECT PROPER NAMES: Identify Armenian proper names (e.g., Ցոլակ, Արսեն, Վարդան).
2. TRANSLITERATE, DO NOT TRANSLATE: 
   - NEVER look for medical or literal meanings in names (e.g., "Ցոլակ" IS NOT "Stool", "Լույս" is NOT "Light").
   - Convert Armenian names to their phonetic English equivalent (e.g., "Ցոլակ" -> "Colak", "Հակոբ" -> "Hakob").
   - Include the transliterated name in `english_translation` so SQL can find it.

TRANSLATION & QUERY EXPANSION PROTOCOL (CRITICAL!):
1. Detect the user's language and store it in `detected_language`.
2. BILINGUAL SEARCH STRINGS: Since the database contains both English and Armenian terms, expansions MUST be bilingual.
3. MEDICAL & STATUS EXPANSION: 
   - DISEASE: "Covid" -> "(COVID-19 OR SARS-CoV-2 OR PCR OR քովիդ OR կորոնավիրուս)"
   - STATUS: "Negative" -> "(negative OR absent OR not detected OR non-reactive OR բացասական OR չի հայտնաբերվել)"
   - Example for "Negative Covid": "(COVID-19 OR SARS-CoV-2 OR քովիդ) AND (negative OR բացասական OR չի հայտնաբերվել)"
4. If the user asks for "ALL patients" without a specific disease, output exactly: "ALL_PATIENTS".
5. Store this string in `english_translation`.
"""

    decision = structured_llm.invoke([
        ("system", system_prompt),
        ("human", f"User Query: {state.get('query', '')}")
    ])

    resolved_patient_id = state.get(
        "patient_id") or decision.extracted_patient_id
    resolved_timeframe = state.get("timeframe") or decision.extracted_timeframe
    resolved_disease = state.get("disease") or decision.extracted_disease

    logger.warning(
        f"Routing: Agent='{decision.target_agent}' | Lang='{decision.detected_language}' | EN_Query='{decision.english_translation}'"
    )

    return {
        "next_node": decision.target_agent,
        "patient_id": resolved_patient_id,
        "query": state.get("query"),
        "english_query": decision.english_translation,
        "user_language": decision.detected_language,
        "timeframe": resolved_timeframe,
        "disease": resolved_disease,
        "needs_pdf": decision.needs_pdf,
        "intermediate_steps": [
            f"🧠 **Օրքեստրատոր**։ Հարցումը վերլուծվեց ({decision.detected_language})։ "
            f"Որոշվեց դիմել `{decision.target_agent}`-ին։ "
            f"Որոնման բանալի՝ \"{decision.english_translation}\""
        ]
    }
