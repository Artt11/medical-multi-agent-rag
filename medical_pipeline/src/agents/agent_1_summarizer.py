from typing import Dict, Any
from sqlalchemy.orm import Session
from src.core.config import llm
from src.core.schemas import MedicalSearchQuery
from src.services.medical_retriever import HybridMedicalRetriever
from src.database.connection import SessionLocal
from src.database.models import PatientModel, MedicalExamModel
from src.utils.logger import get_logger
from src.agents.state import AgentState

logger = get_logger("SUMMARIZER_AGENT")


def summarizer_node(state: AgentState) -> Dict[str, Any]:
    logger.info(
        f"Initiated SUMMARIZER AGENT for query: '{state.get('query', '')}'")

    patient_id = state.get("patient_id", "")
    query_original = state.get("query", "")
    query_en = state.get("english_query", query_original)
    user_lang = state.get("user_language", "Armenian")

    context_blocks = []

    if patient_id:
        logger.debug(
            f"Attempting to fetch recent exams for patient ID: {patient_id}")
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
                    for exam in recent_exams:
                        if exam.full_json:
                            url = exam.source_url or "#"
                            context_blocks.append(
                                f'<record date="{exam.exam_date}" type="{exam.examination_type}" source_url="{url}">\n{exam.full_json}\n</record>'
                            )
                    logger.info(
                        f"Loaded SQL JSON Context: {len(recent_exams)} exams.")
        except Exception as e:
            logger.error(f"Database execution failed: {e}")
        finally:
            db.close()

    if not context_blocks:
        logger.warning(
            "No JSON context found. Falling back to Semantic Vector Search.")
        try:
            retriever = HybridMedicalRetriever()
            search_params = MedicalSearchQuery(
                query_text=query_en, patient_id=patient_id, top_k=10
            )
            chunks = retriever.search(search_params)

            logger.info(
                f"Vector search completed. Retrieved {len(chunks)} chunks.")

            for c in chunks:
                text_content = getattr(c, 'content', getattr(
                    c, 'page_content', '')).strip()
                url = getattr(c, 'blob_url', None)
                if not url and hasattr(c, 'metadata'):
                    url = c.metadata.get('blob_url', '#')

                if text_content:
                    context_blocks.append(
                        f'<chunk source_url="{url}">\n{text_content}\n</chunk>')
        except Exception as e:
            logger.error(f"Vector retrieval failed: {e}")

    context = "\n\n".join(context_blocks)

    system_prompt = f"""
ROLE: Expert Senior Clinical Informatics Specialist.
TASK: Analyze the provided patient records and give a clear, natural summary of their medical status.

CRITICAL RULES:
1. DYNAMIC LANGUAGE: You MUST generate the entire summary strictly in {user_lang}.
2. NO FORCED STRUCTURE: Do NOT use rigid fields. Just write a natural, coherent clinical summary of what is ACTUALLY present in the records. Group findings logically.
3. INLINE CITATION: Every time you mention a test, finding, or result, you MUST append a link to its source file right next to it using this exact format: `[🔗 Դիտել]({{source_url}})` replacing {{source_url}} with the actual link from the tags.
4. GROUNDING: Do not hallucinate. If context is empty, say "Տվյալ պացիենտի վերաբերյալ բժշկական գրառումներ չեն գտնվել:"
"""

    human_message = f"USER QUERY ({user_lang}): {query_original}\n\n<medical_context>\n{context}\n</medical_context>"

    logger.debug(
        f"Invoking LLM for clinical summarization generation in {user_lang}.")
    response = llm.invoke([
        ("system", system_prompt),
        ("human", human_message)
    ])

    logger.info("Summarization successfully completed.")

    return {
        "final_answer": response.content,
        "next_node": "end",
        "intermediate_steps": ["📋 Սամարիզատորը վերլուծեց պացիենտի ամբողջական պատմությունը և պատրաստեց կլինիկական ամփոփագիր:"]
    }
