from typing import Dict, Any
from sqlalchemy.orm import Session
from src.core.config import llm
from src.core.schemas import MedicalSearchQuery
from src.services.medical_retriever import HybridMedicalRetriever
from src.database.connection import SessionLocal
from src.database.models import PatientModel, MedicalExamModel


def summarizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- 🤖 SUMMARIZER AGENT (Optimized for JSON & RAG) ---")

    patient_id = state.get("patient_id", "")
    query_text = state["query"]
    context = ""
    source_urls = set()

    # 1. SQL-FIRST LOGIC
    if patient_id:
        db: Session = SessionLocal()
        try:
            patient = db.query(PatientModel).filter(
                (PatientModel.patient_id == patient_id) |
                (PatientModel.social_card == patient_id)
            ).first()

            if patient:
                recent_exams = db.query(MedicalExamModel).filter(
                    MedicalExamModel.patient_id == patient.id
                ).order_by(MedicalExamModel.exam_date.desc()).limit(3).all()

                if recent_exams:
                    json_contexts = []
                    for exam in recent_exams:
                        if exam.full_json:
                            # Օգտագործում ենք XML-ատիպ տեգեր կոնտեքստը LLM-ի համար ավելի ընկալելի դարձնելու համար
                            json_contexts.append(
                                f"<record>\n<date>{exam.exam_date}</date>\n<type>{exam.examination_type}</type>\n<raw_data>{exam.full_json}</raw_data>\n</record>")
                        if exam.source_url:
                            source_urls.add(exam.source_url)

                    if json_contexts:
                        context = "\n".join(json_contexts)
                        print("--- ⚡ LOG: SQL JSON Context Loaded ---")
        except Exception as e:
            print(f"--- ⚠️ LOG: SQL Error: {e} ---")
        finally:
            db.close()

    # 2. FALLBACK TO VECTOR SEARCH
    if not context:
        print("--- 🔍 LOG: Falling back to Vector Search ---")
        retriever = HybridMedicalRetriever()
        search_params = MedicalSearchQuery(
            query_text=query_text, patient_id=patient_id, top_k=5)
        chunks = retriever.search(search_params)
        context = "\n\n".join(
            [f"<chunk>{c.page_content}</chunk>" for c in chunks])
        for c in chunks:
            if c.blob_url:
                source_urls.add(c.blob_url)

    # 3. IMPROVED LLM PROMPT
    # Ավելացրել եմ Chain-of-Thought (հրահանգ՝ նախ վերլուծել, հետո գրել) և JSON մշակման կանոններ
    system_prompt = (
        """ROLE:
You are an expert Senior Clinical Informatics Specialist. Your task is to analyze medical data and provide a precise clinical summary.

DATA HANDLING:
The provided context may contain raw JSON structures or OCR-extracted text. 
- If JSON: Map keys to clinical meanings (e.g., "val" -> value, "ref" -> reference range).
- If OCR: Ignore formatting errors and focus on medical entities.

INSTRUCTIONS:
1. **Analyze**: Carefully scan the data for diagnoses, abnormal lab values (flagged as 'high', 'low', '*', or outside reference ranges), and doctor recommendations.
2. **Synthesize**: Create a summary that reflects the patient's current health status based ONLY on the provided records.
3. **Verify**: Ensure all measurements include their respective units (e.g., mg/dL, mmol/L).

STRICT RULES:
- **Grounding**: Do not include information NOT found in the context.
- **No Hallucinations**: If a value is missing, state "Not specified". 
- **Language**: If the User Query is in Armenian, provide the summary in Armenian. If in English, provide it in English.
- **Empty State**: If context is insufficient, return: "Insufficient medical records available to provide a summary."

OUTPUT STRUCTURE:
## Clinical Summary

**Primary Diagnosis:** 
<diagnosis or "Not specified">

**Key Abnormal Findings:**
- <finding 1 with values/units>
- <finding 2 with values/units>

**Physician Conclusion & Impression:**
<concise summary of doctor's final words>

**Additional Clinical Notes:**
<relevant details like follow-up dates or specific warnings or "None">"""
    )

    human_message = f"USER QUERY: {query_text}\n\n<medical_context>\n{context}\n</medical_context>"

    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    # 4. Source Block Formatting
    source_block = ""
    if source_urls:
        source_block = "\n\n🔗 **Կից փաստաթղթեր / Source Documents:**\n" + "\n".join(
            [f"- [Դիտել ֆայլը]({url})" for url in source_urls])

    return {
        "final_answer": response.content + source_block,
        "context_chunks": [context]
    }
