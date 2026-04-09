
# from typing import Dict, Any
# from src.core.config import llm
# from src.core.schemas import MedicalSearchQuery
# from src.services.medical_retriever import HybridMedicalRetriever
# # ՀԵՌԱՑՎԵԼ Է: source_link_service-ի ներմուծումը


# def comparative_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("--- ⚖️ COMPARATIVE ANALYST AGENT (Agent 5) ---")

#     retriever = HybridMedicalRetriever()

#     search_params = MedicalSearchQuery(
#         query_text=state["query"],
#         patient_id=state.get("patient_id"),
#         top_k=10
#     )

#     chunks = retriever.search(search_params)

#     # Կառուցում ենք կոնտեքստը՝ օգտագործելով chunk-երի մետատվյալների ամսաթվերը
#     context = "\n\n".join([
#         f"Document Date: {c.metadata.get('exam_date', 'Unknown Date')}\nContent: {c.page_content}"
#         for c in chunks
#     ])

#     system_prompt = """
# ROLE
# You are a Senior Clinical Comparative Analysis Agent.
# Your responsibility is to analyze and compare a patient's medical findings across multiple time periods using only the retrieved medical context.

# STRICT GROUNDING RULE
# You MUST rely ONLY on the provided context. Do not invent values or conclusions.

# OUTPUT STRUCTURE
# Temporal Clinical Comparison
# - Metric or Condition
# - Time Period 1 (Date & Finding)
# - Time Period 2 (Date & Finding)
# - Trend Assessment (Improved / Deteriorated / Stable)
# - Clinical Conclusion
# """

#     human_message = f"Chronological Medical Context:\n{context}\n\nUser Query: {state['query']}"

#     response = llm.invoke([
#         ("system", system_prompt),
#         ("human", human_message)
#     ])

#     # Հավաքում ենք Google Drive հղումները անմիջապես chunk-երի միջից
#     # Մեր նոր Orchestrator-ը Drive URL-ը պահում է որպես blob_url
#     source_urls = set()
#     for c in chunks:
#         url = c.metadata.get("blob_url") or getattr(c, 'blob_url', None)
#         if url:
#             source_urls.add(url)

#     # Ձևավորում ենք հղումների բլոկը
#     source_block = ""
#     if source_urls:
#         source_block = "\n\n🔗 **Source Documents (Google Drive):**\n" + "\n".join(
#             [f"- [Դիտել Ֆայլը]({url})" for url in source_urls]
#         )

#     return {
#         "final_answer": response.content + source_block,
#         "context_chunks": [context]
#     }
from typing import Dict, Any
from src.core.config import llm
from src.core.schemas import MedicalSearchQuery
from src.services.medical_retriever import HybridMedicalRetriever


def comparative_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- ⚖️ COMPARATIVE ANALYST AGENT (Agent 5 - Optimized) ---")

    retriever = HybridMedicalRetriever()
    user_query = state.get("query", "")

    search_params = MedicalSearchQuery(
        query_text=user_query,
        patient_id=state.get("patient_id"),
        top_k=10
    )

    chunks = retriever.search(search_params)

    # ==========================================
    # 1. OPTIMIZED CONTEXT FORMATTING (XML-like)
    # ==========================================
    # Ավելացնում ենք <record> տեգեր և հստակ առանձնացնում ամսաթվերը
    context_blocks = []
    for i, c in enumerate(chunks):
        date = c.metadata.get('exam_date', 'Unknown Date')
        content = c.page_content.strip()
        context_blocks.append(
            f"<record index=\"{i+1}\" date=\"{date}\">\n{content}\n</record>")

    context_text = "\n\n".join(context_blocks)

    # ==========================================
    # 2. OPTIMIZED SYSTEM PROMPT
    # ==========================================
    system_prompt = """
ROLE:
You are an Expert Clinical Comparative Analyst. 
Your task is to analyze a patient's medical records across different dates, identify chronological trends, and evaluate if their clinical metrics are improving, deteriorating, or stable.

<rules>
1. STRICT GROUNDING: Rely ONLY on the information within the `<record>` tags. Do not hallucinate previous baseline values.
2. CHRONOLOGICAL REASONING: Always map findings to their respective dates. Compare older dates (baseline) to newer dates (follow-up).
3. INSUFFICIENT DATA HANDLING: If the retrieved records all belong to the same date, or if there is no overlapping metric to compare, clearly state: "Բավարար ժամանակագրական տվյալներ չկան դինամիկան համեմատելու համար:" (Insufficient data for comparison).
4. LANGUAGE: Generate the final response STRICTLY in Armenian.
5. FORMATTING: Use a Markdown Table for the comparison. It is mandatory for readability.
</rules>

OUTPUT STRUCTURE:
### ⚖️ Կլինիկական Դինամիկայի Վերլուծություն

**Ամփոփում:**
<Հակիրճ նկարագրություն հայտնաբերված տրենդի մասին>

**Համեմատական Աղյուսակ:**
| Ցուցանիշ / Պարամետր | Նախորդ Արդյունք ([Ամսաթիվ 1]) | Նոր Արդյունք ([Ամսաթիվ 2]) | Դինամիկա |
| :--- | :--- | :--- | :--- |
| <Metric Name> | <Value/Observation> | <Value/Observation> | 🟢 Բարելավում / 🔴 Վատթարացում / ⚪ Կայուն |

**Եզրակացություն:**
<Ընդհանուր բժշկական եզրահանգում միայն առկա տվյալների հիման վրա>
"""

    human_message = f"USER QUERY: {user_query}\n\n<medical_records>\n{context_text}\n</medical_records>"

    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    # ==========================================
    # 3. SOURCE URLS HANDLING
    # ==========================================
    source_urls = set()
    for c in chunks:
        url = c.metadata.get("blob_url") or getattr(c, 'blob_url', None)
        if url:
            source_urls.add(str(url))

    source_block = ""
    if source_urls:
        source_block = "\n\n🔗 **Կից փաստաթղթեր (Google Drive):**\n" + "\n".join(
            [f"- [Դիտել Ֆայլը]({url})" for url in source_urls]
        )

    return {
        "final_answer": response.content + source_block,
        "context_chunks": [context_text]
    }
