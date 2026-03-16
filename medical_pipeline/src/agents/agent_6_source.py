# from typing import Dict, Any
# from src.core.config import llm
# from src.core.schemas import MedicalSearchQuery
# from src.services.medical_retriever import HybridMedicalRetriever


# def source_retriever_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("--- 🔗 SOURCE RETRIEVER AGENT (Agent 6) ---")

#     retriever = HybridMedicalRetriever()

#     search_params = MedicalSearchQuery(
#         query_text=state["query"],
#         patient_id=state.get("patient_id", ""),
#         top_k=5
#     )

#     chunks = retriever.search(search_params)

#     links_data = []
#     for c in chunks:
#         url = c.metadata.get("blob_url", "No URL available")
#         doc_hash = c.metadata.get("doc_hash", "Unknown Hash")
#         if url not in [link['url'] for link in links_data]:
#             links_data.append({"url": url, "hash": doc_hash})

#     context_str = "\n".join([
#         f"Document Hash: {item['hash']}\nAccess Link: {item['url']}"
#         for item in links_data
#     ])

#     system_prompt = (
#         "You are a Medical Records Archivist. Your sole responsibility is to "
#         "provide the user with the direct source links (URLs) to the requested medical examination files.\n\n"
#         "Guidelines:\n"
#         "1. Present the links in a clear, professional bulleted list.\n"
#         "2. Include the Document Hash alongside the link for auditability.\n"
#         "3. DO NOT attempt to summarize the medical content or diagnose the patient. Only provide the access links.\n"
#         "4. If no links are found in the context, state: 'No source files were found matching your criteria.'"
#     )

#     human_message = f"Available Archival Links:\n{context_str}\n\nUser Query: {state['query']}"

#     response = llm.invoke([
#         ("system", system_prompt),
#         ("human", human_message)
#     ])

#     return {
#         "final_answer": response.content,
#         "context_chunks": [context_str]
#     }
from typing import Dict, Any
from src.core.config import llm
from src.core.schemas import MedicalSearchQuery
from src.services.medical_retriever import HybridMedicalRetriever
from src.services.source_link_service import build_pdf_url


def source_retriever_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- 🔗 SOURCE RETRIEVER AGENT (Agent 6) ---")

    retriever = HybridMedicalRetriever()

    search_params = MedicalSearchQuery(
        query_text=state["query"],
        patient_id=state.get("patient_id"),
        top_k=5
    )

    chunks = retriever.search(search_params)

    links_data = []
    for c in chunks:
        doc_hash = getattr(c, "document_hash", None) or c.metadata.get("doc_hash")
        url = getattr(c, "blob_url", None) or c.metadata.get("blob_url")
        if not url and doc_hash:
            url = build_pdf_url(str(doc_hash))
        if not url:
            continue
        if url not in [link["url"] for link in links_data]:
            links_data.append({"url": url, "hash": doc_hash or "Unknown Hash"})

    context_str = "\n".join([
        f"Document Hash: {item['hash']}\nAccess Link: {item['url']}"
        for item in links_data
    ])

    system_prompt = """
ROLE
You are a Medical Records Source Retrieval Agent.

Your responsibility is to provide the user with direct access links
to the original medical documents stored in the archive.

--------------------------------------------------

INPUT

You will receive a list of archival document references that include:

• Document Hash
• Access Link (URL)

These links correspond to the original medical records retrieved
by the system.

--------------------------------------------------

TASK

Return the available source links so the user can directly access
the original medical examination documents.

--------------------------------------------------

STRICT RULES

1. SOURCE GROUNDING
Use ONLY the links provided in the context.

2. NO HALLUCINATED LINKS
Do not generate, modify, or guess URLs.

3. NO MEDICAL INTERPRETATION
Do not summarize medical findings.
Do not analyze medical data.
Do not provide diagnoses.

4. DEDUPLICATION
If duplicate links exist, list each unique link only once.

5. EMPTY RESULT HANDLING
If no valid links exist in the context, respond exactly with:

No source files were found matching your criteria.

--------------------------------------------------

OUTPUT FORMAT

Source Medical Documents

• Document Hash: <hash>
  Access Link: <url>

• Document Hash: <hash>
  Access Link: <url>

Return only the formatted list of links.
Do not include explanations.
"""

    human_message = f"Available Archival Links:\n{context_str}\n\nUser Query: {state['query']}"

    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    return {
        "final_answer": response.content,
        "context_chunks": [context_str]
    }
