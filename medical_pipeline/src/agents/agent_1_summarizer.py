# from typing import Dict, Any
# from src.core.config import llm
# from src.core.schemas import MedicalSearchQuery
# from src.services.medical_retriever import HybridMedicalRetriever
# from src.services.source_link_service import build_pdf_urls, format_source_links


# def summarizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("---SUMMARIZER AGENT (Agent 1) ---")

#     retriever = HybridMedicalRetriever()

#     search_params = MedicalSearchQuery(
#         query_text=state["query"],
#         patient_id=state.get("patient_id", ""),
#         top_k=5
#     )
#     chunks = retriever.search(search_params)
#     context = "\n\n".join([c.page_content for c in chunks])
#     system_prompt = (
#         """ROLE
# You are a ** Clinical Report Summarization Agent ** operating inside a Retrieval-Augmented Generation(RAG) system.

# Your responsibility is to generate a ** clear, accurate, and concise clinical summary ** of a patient's medical examination report using **only the retrieved context**.

# ---

# INPUT
# You will receive:

# Context:
# Medical text retrieved from a knowledge base, which may include:

# * physician notes
# * laboratory results
# * diagnostic reports
# * OCR-extracted medical documents

# The context may contain **noise, partial sentences, or formatting errors**.

# ---

# OBJECTIVE

# Extract and summarize the most clinically relevant information from the context, including:

# • Primary diagnosis (if present)
# • Critical abnormal laboratory values
# • Key clinical observations
# • Physician’s conclusion or impression

# The summary must be **clinically precise and easy for medical professionals to read**.

# ---

# STRICT RULES

# 1. **Grounding Requirement**
#    Every statement in the summary must come directly from the provided context.

# 2. **Zero Hallucination Policy**
#    Do not invent diagnoses, values, symptoms, treatments, or conclusions.

# 3. **No External Knowledge**
#    Do not use prior knowledge or assumptions. Use only the retrieved text.

# 4. **Incomplete Context Handling**
#    If the context is empty or lacks enough medical information, respond exactly with:

# Insufficient medical records available to provide a summary.

# 5. **Clinical Terminology**
#    Use professional medical terminology appropriate for physicians.

# 6. **Prioritize Important Findings**
#    Highlight abnormal laboratory results, confirmed diagnoses, and physician conclusions.

# ---

# OUTPUT FORMAT

# Clinical Summary

# Primary Diagnosis:
# <diagnosis or "Not specified">

# Key Abnormal Findings:
# • <finding>
# • <finding>

# Physician Conclusion / Impression:

# <summary or "Not specified">

# Additional Notes:
# <optional clinically relevant information or "None">

# ---

# QUALITY STANDARD

# The output must be:

# • Factually grounded in the context
# • Clinically accurate
# • Concise and structured
# • Free of speculation"""
#     )

#     human_message = f"Medical Context:\n{context}\n\nUser Query: {state['query']}"

#     response = llm.invoke([
#         ("system", system_prompt),
#         ("human", human_message)
#     ])

#     blob_urls = [c.blob_url for c in chunks if c.blob_url]
#     doc_hashes = [c.document_hash for c in chunks if c.document_hash]
#     source_block = format_source_links(blob_urls + build_pdf_urls(doc_hashes))

#     return {
#         "final_answer": response.content + source_block,
#         "context_chunks": [context]
#     }
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.core.config import llm
from src.core.schemas import MedicalSearchQuery
from src.services.medical_retriever import HybridMedicalRetriever
from src.database.connection import SessionLocal
from src.database.models import PatientModel, MedicalExamModel


def summarizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- 🤖 SUMMARIZER AGENT (Agent 1 - SQL First) ---")

    patient_id = state.get("patient_id", "")
    query_text = state["query"]
    context = ""
    source_urls = set()

    # ==========================================
    # 1. SQL-FIRST LOGIC (ՆՈՐ ԱՐԱԳ ՄՈՏԵՑՈՒՄ)
    # ==========================================
    if patient_id:
        db: Session = SessionLocal()
        try:
            # Փնտրում ենք պացիենտին բազայում
            patient = db.query(PatientModel).filter(
                (PatientModel.patient_id == patient_id) |
                (PatientModel.social_card == patient_id)
            ).first()

            if patient:
                # Վերցնում ենք վերջին 3 հետազոտությունների ԱՄԲՈՂՋԱԿԱՆ JSON-ները
                recent_exams = db.query(MedicalExamModel).filter(
                    MedicalExamModel.patient_id == patient.id
                ).order_by(MedicalExamModel.exam_date.desc()).limit(3).all()

                if recent_exams:
                    json_contexts = []
                    for exam in recent_exams:
                        if exam.full_json:
                            # Որպես կոնտեքստ տալիս ենք մաքուր JSON-ը
                            json_contexts.append(
                                f"Date: {exam.exam_date} | Type: {exam.examination_type}\nData: {exam.full_json}")
                        if exam.source_url:
                            source_urls.add(exam.source_url)

                    if json_contexts:
                        context = "\n\n---\n\n".join(json_contexts)
                        print(
                            "--- ⚡ LOG: Կոնտեքստը վերցվեց SQL բազայի մաքուր JSON-ից ---")
        except Exception as e:
            print(f"--- ⚠️ LOG: SQL սխալ, անցնում ենք RAG-ի: {e} ---")
        finally:
            db.close()

    # ==========================================
    # 2. FALLBACK TO VECTOR SEARCH (ՀԻՆ RAG ՄՈՏԵՑՈՒՄԸ)
    # ==========================================
    if not context:
        print("--- 🔍 LOG: Անցնում ենք Vector Search-ի (Hybrid Retrieval) ---")
        retriever = HybridMedicalRetriever()

        search_params = MedicalSearchQuery(
            query_text=query_text,
            patient_id=patient_id,
            top_k=5
        )
        chunks = retriever.search(search_params)
        context = "\n\n".join([c.page_content for c in chunks])

        for c in chunks:
            # Եթե մեր նոր համակարգը chunk-ի մեջ դրել է blob_url (որն արդեն Drive-ի url-ն է)
            if c.blob_url:
                source_urls.add(c.blob_url)

    # ==========================================
    # 3. LLM PROMPT (ՔՈ ԳՐԱԾ ՊՐՈՄՓԹԸ ԱՆՓՈՓՈԽ)
    # ==========================================
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

    human_message = f"Medical Context:\n{context}\n\nUser Query: {query_text}"

    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    # 4. Սարքում ենք Google Drive հղումների բլոկը
    if source_urls:
        source_block = "\n\n🔗 **Source Documents (Google Drive):**\n" + "\n".join(
            [f"- [Դիտել Ֆայլը]({url})" for url in source_urls])
    else:
        source_block = ""

    return {
        "final_answer": response.content + source_block,
        "context_chunks": [context]
    }
