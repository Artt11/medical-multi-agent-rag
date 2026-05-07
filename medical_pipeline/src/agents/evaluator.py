from typing import Dict, Any
from src.core.config import llm
from src.utils.logger import get_logger
from src.agents.state import AgentState

logger = get_logger("EVALUATOR_AGENT")


def evaluator_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Initiating EVALUATOR AGENT for data synthesis.")

    results = state.get("sql_results", [])
    user_lang = state.get("user_language", "Armenian")
    query = state.get("query", "")

    if not results:
        logger.warning("No SQL results found. Returning empty state message.")
        return {
            "final_answer": f"Տվյալների բազայում «{query}» հարցման վերաբերյալ գրառումներ չեն գտնվել:",
            "next_node": "end"
        }

    system_prompt = f"""
ROLE: Expert Medical Data Synthesizer.
TASK: Convert the raw database results into a clear, clinical summary report.

<rules>
1. DYNAMIC LANGUAGE: You MUST write the entire response strictly in {user_lang}.
2. FORMATTING: Present the patient data using a clean, professional Markdown table. Include relevant columns based on the data provided (e.g., Patient, ID, Diagnosis, Date).
3. SOURCE LINKS: If `source_url` is present in the data, you MUST add a column (e.g., 'Source' or 'Ֆայլ') and format the link precisely as `[🔗 Դիտել](source_url)`.
4. NO TRUNCATION: You must include ALL rows provided in the results array. Do not skip any patients.
5. PROFESSIONAL TONE: Add a brief introductory sentence summarizing what was found.
</rules>
"""
    logger.debug(f"Invoking LLM for table generation in {user_lang}.")
    response = llm.invoke([
        ("system", system_prompt),
        ("human", f"User Query: {query}\n\nRAW DATA:\n{results}")
    ])

    return {
        "final_answer": response.content,
        "next_node": "end",
        "intermediate_steps": ["✨ Evaluator-ը համադրեց SQL-ից ստացված տվյալները և ձևավորեց վերջնական հաշվետվությունը:"]
    }
