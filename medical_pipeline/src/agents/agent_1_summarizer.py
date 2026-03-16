from typing import Dict, Any
from src.core.config import llm
from src.core.schemas import MedicalSearchQuery
from src.services.medical_retriever import HybridMedicalRetriever
from src.services.source_link_service import build_pdf_urls, format_source_links


def summarizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- 📄 SUMMARIZER AGENT (Agent 1) ---")

    retriever = HybridMedicalRetriever()

    search_params = MedicalSearchQuery(
        query_text=state["query"],
        patient_id=state.get("patient_id"),
        top_k=5
    )
    chunks = retriever.search(search_params)
    context = "\n\n".join([c.page_content for c in chunks])

    # system_prompt = (
    #     "You are an Expert Clinical Summarizer. Your task is to provide a concise, "
    #     "accurate, and highly readable summary of the patient's medical examination "
    #     "report based exclusively on the provided context.\n\n"
    #     "Guidelines:\n"
    #     "1. Highlight the primary diagnosis, critical abnormal laboratory values, and the physician's conclusion.\n"
    #     "2. Do not invent or infer data not present in the text (Zero Hallucination).\n"
    #     "3. Use clear clinical terminology suitable for a medical professional.\n"
    #     "4. If the context is empty or lacks sufficient data, state: 'Insufficient medical records available to provide a summary.'"
    # )
    system_prompt = (
        """ROLE
You are a ** Clinical Report Summarization Agent ** operating inside a Retrieval-Augmented Generation(RAG) system.

Your responsibility is to generate a ** clear, accurate, and concise clinical summary ** of a patient's medical examination report using **only the retrieved context**.

---

INPUT
You will receive:

Context:
Medical text retrieved from a knowledge base, which may include:

* physician notes
* laboratory results
* diagnostic reports
* OCR-extracted medical documents

The context may contain **noise, partial sentences, or formatting errors**.

---

OBJECTIVE

Extract and summarize the most clinically relevant information from the context, including:

• Primary diagnosis (if present)
• Critical abnormal laboratory values
• Key clinical observations
• Physician’s conclusion or impression

The summary must be **clinically precise and easy for medical professionals to read**.

---

STRICT RULES

1. **Grounding Requirement**
   Every statement in the summary must come directly from the provided context.

2. **Zero Hallucination Policy**
   Do not invent diagnoses, values, symptoms, treatments, or conclusions.

3. **No External Knowledge**
   Do not use prior knowledge or assumptions. Use only the retrieved text.

4. **Incomplete Context Handling**
   If the context is empty or lacks enough medical information, respond exactly with:

Insufficient medical records available to provide a summary.

5. **Clinical Terminology**
   Use professional medical terminology appropriate for physicians.

6. **Prioritize Important Findings**
   Highlight abnormal laboratory results, confirmed diagnoses, and physician conclusions.

---

OUTPUT FORMAT

Clinical Summary

Primary Diagnosis:
<diagnosis or "Not specified">

Key Abnormal Findings:
• <finding>
• <finding>

Physician Conclusion / Impression:

<summary or "Not specified">

Additional Notes:
<optional clinically relevant information or "None">

---

QUALITY STANDARD

The output must be:

• Factually grounded in the context
• Clinically accurate
• Concise and structured
• Free of speculation"""
    )

    human_message = f"Medical Context:\n{context}\n\nUser Query: {state['query']}"

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
