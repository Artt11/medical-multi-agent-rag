# from typing import Dict, Any
# from src.core.config import llm
# from src.core.schemas import MedicalSearchQuery
# from src.services.medical_retriever import HybridMedicalRetriever


# def comparative_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("--- ⚖️ COMPARATIVE ANALYST AGENT (Agent 5) ---")

#     retriever = HybridMedicalRetriever()

#     search_params = MedicalSearchQuery(
#         query_text=state["query"],
#         patient_id=state.get("patient_id", ""),
#         top_k=10
#     )

#     chunks = retriever.search(search_params)

#     context = "\n\n".join([
#         f"Document Date: {c.metadata.get('exam_date', 'Unknown Date')}\nContent: {c.page_content}"
#         for c in chunks
#     ])

#     system_prompt = (
#         "You are a Senior Clinical Comparative Analyst. Your objective is to compare "
#         "a single patient's medical laboratory results and clinical conditions across "
#         "different time periods (e.g., Time X vs. Time Y).\n\n"
#         "Operational Guidelines:\n"
#         "1. Identify and extract the specific metrics (e.g., glucose, vitamin D) from the provided context.\n"
#         "2. Compare the values chronologically. State clearly whether the condition has improved, deteriorated, or remained stable.\n"
#         "3. STRICT GROUNDING: Rely ONLY on the provided context.\n"
#         "4. If data for one of the requested time periods is missing, state: 'Insufficient temporal data for a complete comparison.'\n"
#         "5. Structure your output with clear headings for each time period and a 'Clinical Conclusion' section."
#     )

#     human_message = f"Chronological Medical Context:\n{context}\n\nUser Query: {state['query']}"

#     response = llm.invoke([
#         ("system", system_prompt),
#         ("human", human_message)
#     ])

#     return {
#         "final_answer": response.content,
#         "context_chunks": [context]
#     }
from typing import Dict, Any
from src.core.config import llm
from src.core.schemas import MedicalSearchQuery
from src.services.medical_retriever import HybridMedicalRetriever
from src.services.source_link_service import build_pdf_urls, format_source_links


def comparative_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- ⚖️ COMPARATIVE ANALYST AGENT (Agent 5) ---")

    retriever = HybridMedicalRetriever()

    search_params = MedicalSearchQuery(
        query_text=state["query"],
        patient_id=state.get("patient_id"),
        top_k=10
    )

    chunks = retriever.search(search_params)

    context = "\n\n".join([
        f"Document Date: {c.metadata.get('exam_date', 'Unknown Date')}\nContent: {c.page_content}"
        for c in chunks
    ])

    system_prompt = """
ROLE
You are a Senior Clinical Comparative Analysis Agent.

Your responsibility is to analyze and compare a patient's medical findings
across multiple time periods using only the retrieved medical context.

--------------------------------------------------

INPUT

You will receive chronological medical context retrieved from
clinical documents such as laboratory reports, examination notes,
or diagnostic summaries.

Each document includes:
- Document Date
- Medical content

--------------------------------------------------

TASK

Perform a temporal comparison of the patient's clinical metrics
or medical conditions across the different time periods.

Focus on identifying:

• laboratory values
• clinical diagnoses
• relevant biomarkers
• measurable medical indicators

--------------------------------------------------

STRICT GROUNDING RULE

You MUST rely ONLY on the provided context.
Do not invent laboratory values, diagnoses, or medical conclusions.

If the context does not contain sufficient information
for comparison between time periods, respond with:

"Insufficient temporal data for a complete comparison."

--------------------------------------------------

COMPARISON REQUIREMENTS

1. Identify relevant medical metrics in the context.
2. Compare them chronologically.
3. Determine whether the patient's condition has:

- Improved
- Deteriorated
- Remained stable

4. Clearly reference the dates associated with the findings.

--------------------------------------------------

OUTPUT STRUCTURE

Temporal Clinical Comparison

Metric or Condition:
<name of metric or diagnosis>

Time Period 1:
<date and finding>

Time Period 2:
<date and finding>

Trend Assessment:
<Improved / Deteriorated / Stable>

Clinical Conclusion:
<brief professional interpretation>

--------------------------------------------------

QUALITY STANDARD

The analysis must be:
• medically clear
• strictly grounded in the provided context
• chronologically accurate
"""

    human_message = f"Chronological Medical Context:\n{context}\n\nUser Query: {state['query']}"

    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    blob_urls = [c.blob_url for c in chunks if c.blob_url]
    doc_hashes = [c.document_hash for c in chunks if c.document_hash]
    source_block = format_source_links(blob_urls + build_pdf_urls(doc_hashes))

    return {
        "final_answer": response.content + source_block,
        "context_chunks": [context]
    }
