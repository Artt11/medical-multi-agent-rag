from typing import Dict, Any
from src.core.config import llm
from src.core.schemas import MedicalSearchQuery
from src.services.medical_retriever import HybridMedicalRetriever
from src.utils.logger import get_logger
from src.agents.state import AgentState  # 👈 Ներմուծում ենք AgentState-ը

logger = get_logger("COMPARATIVE_AGENT")


def comparative_node(state: AgentState) -> Dict[str, Any]:  # 👈 Տիպայնացում
    logger.info(
        f"Initiated COMPARATIVE AGENT for query: '{state.get('query', '')}'")

    patient_id = state.get("patient_id", "")
    query_original = state.get("query", "")
    query_en = state.get("english_query", query_original)
    user_lang = state.get("user_language", "Armenian")

    retriever = HybridMedicalRetriever()

    search_params = MedicalSearchQuery(
        query_text=query_en,
        patient_id=patient_id,
        top_k=15
    )

    logger.debug(f"Executing vector search. Patient ID: {patient_id}")
    chunks = retriever.search(search_params)
    logger.info(
        f"Retrieved {len(chunks)} chunks for chronological comparison.")

    context_blocks = []
    for c in chunks:
        date = c.metadata.get('exam_date', 'Unknown Date') if hasattr(
            c, 'metadata') else 'Unknown Date'
        text_content = getattr(c, 'content', getattr(
            c, 'page_content', '')).strip()

        url = getattr(c, 'blob_url', None)
        if not url and hasattr(c, 'metadata'):
            url = c.metadata.get('blob_url', '#')

        if text_content:
            context_blocks.append(
                f'<record date="{date}" source_url="{url}">\n{text_content}\n</record>')

    context = "\n\n".join(context_blocks)

    system_prompt = f"""
ROLE: Expert Clinical Data Analyst.
TASK: Compare medical records over time to identify trends, improvements, or deteriorations.

CRITICAL RULES:
1. DYNAMIC LANGUAGE: You MUST generate the entire analysis strictly in {user_lang}.
2. FLEXIBLE LOGIC (NO FORCED TABLES):
   - If you find data from DIFFERENT dates for the same metric, create a clear Markdown comparison table.
   - If there is only ONE record, or no comparable overlapping data, DO NOT generate a table with "N/A". Instead, write a natural text explanation in {user_lang} stating that chronological comparison is impossible due to lack of multiple dates, and simply summarize what WAS found.
3. INLINE CITATION: Every time you mention a specific result or date, you MUST append the link to its source file using this format: `[🔗 Դիտել]({{source_url}})` replacing {{source_url}} with the actual link from the `<record>` tag.
4. GROUNDING: Base all comparisons strictly on the provided `<medical_context>`.
"""

    human_message = f"USER QUERY ({user_lang}): {query_original}\n\n<medical_context>\n{context}\n</medical_context>"

    logger.debug(f"Invoking LLM for chronological comparison in {user_lang}.")
    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    logger.info("Comparative analysis successfully completed.")

    return {
        "final_answer": response.content,
        "next_node": "end",
        "intermediate_steps": ["⚖️ Համեմատական ագենտը վերլուծեց կլինիկական տվյալների դինամիկան տարբեր ամսաթվերի միջև:"]
    }
