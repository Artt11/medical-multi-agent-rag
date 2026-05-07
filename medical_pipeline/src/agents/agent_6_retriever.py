from typing import Dict, Any
from src.core.config import llm
from src.core.schemas import MedicalSearchQuery
from src.services.medical_retriever import HybridMedicalRetriever
from src.utils.logger import get_logger
from src.agents.state import AgentState

logger = get_logger("VECTOR_RETRIEVER")


def medical_retriever_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Initializing Semantic Vector Retriever Agent.")

    query_original = state.get("query", "")
    query_en = state.get("english_query", query_original)
    user_lang = state.get("user_language", "Armenian")
    patient_id = state.get("patient_id")

    dynamic_top_k = 10 if patient_id else 50

    retriever = HybridMedicalRetriever()
    search_params = MedicalSearchQuery(
        query_text=query_en,
        patient_id=patient_id,
        top_k=dynamic_top_k
    )

    logger.debug(
        f"Executing HNSW vector search with top_k={dynamic_top_k} for query: '{query_en}'")
    chunks = retriever.search(search_params)
    logger.info(f"Retrieved {len(chunks)} relevant medical chunks.")

    context_blocks = []

    for i, c in enumerate(chunks):
        text_content = getattr(c, 'content', getattr(
            c, 'page_content', '')).strip()

        chunk_patient_id = getattr(c, 'patient_id', 'Unknown ID')
        if chunk_patient_id == 'Unknown ID' and hasattr(c, 'metadata'):
            chunk_patient_id = c.metadata.get('patient_id', 'Unknown ID')

        url = getattr(c, 'blob_url', None)
        if not url and hasattr(c, 'metadata'):
            url = c.metadata.get('blob_url', 'No Link')

        if text_content:
            context_blocks.append(
                f'<chunk id="{i}" patient_id="{chunk_patient_id}" source_url="{url}">\n{text_content}\n</chunk>'
            )

    context = "\n\n".join(context_blocks)

    system_prompt = f"""
ROLE: Expert Clinical RAG Assistant.
TASK: Answer the user's medical query using ONLY the provided English document chunks.

CRITICAL RULES:
1. MULTI-CONDITION EXTRACT: If the user asks for multiple conditions (e.g., "Pneumonia OR Vitamin D"), you MUST extract and list patients for ALL mentioned conditions. Do not drop any condition.
2. STRICT FILTERING: Only extract and summarize information that EXACTLY matches the user's query. Ignore any diseases, symptoms, or data that were not explicitly asked for.
3. CITATION & LINKING: When providing an answer or listing patients, you MUST include their `patient_id` and the explicit `source_url` provided in their `<chunk>` tag.
4. DYNAMIC LANGUAGE: You MUST generate the final answer strictly in {user_lang}. Accurately translate clinical findings from the English context to {user_lang}.
5. NO HALLUCINATION: If the requested information is not in the chunks, explicitly state: "No relevant information found."

OUTPUT FORMATTING:
- If listing multiple patients/cases, use this exact bullet format:
  * **Patient [ID]**: [Brief explanation of finding] - [🔗 Document](source_url)
- If answering for a single patient, provide the clinical answer and append the link at the end.
"""

    human_message = f"USER QUERY ({user_lang}): {query_original}\n\n<medical_documents>\n{context}\n</medical_documents>"

    logger.debug(f"Invoking LLM to generate targeted response in {user_lang}.")
    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    logger.info("Semantic retrieval and generation complete.")

    return {
        "final_answer": response.content,
        "context_chunks": [context],
        "next_node": "end",
        "intermediate_steps": [f"🔍 Retriever-ը գտավ {len(chunks)} համապատասխան հատված բժշկական փաստաթղթերից:"]
    }
