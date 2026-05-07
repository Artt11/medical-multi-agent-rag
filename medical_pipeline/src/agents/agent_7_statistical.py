import re
from typing import Dict, Any
from sqlalchemy import text
from src.core.config import llm
from src.core.schemas import SqlQueryOutput
from src.database.connection import SessionLocal
from src.utils.logger import get_logger
from src.agents.state import AgentState

logger = get_logger("SQL_ENGINE")


def is_safe_sql(sql_query: str) -> bool:
    forbidden_pattern = re.compile(
        r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|EXEC|MERGE|GRANT|REVOKE)\b',
        re.IGNORECASE
    )
    return not bool(forbidden_pattern.search(sql_query))


def statistical_filter_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Initializing SQL Engine for structured data retrieval.")

    db = SessionLocal()
    query_en = state.get("english_query", state.get("query", ""))
    extracted_timeframe = state.get("timeframe") or "None specified"
    extracted_patient_id = state.get("patient_id") or "None specified"

    structured_llm = llm.with_structured_output(SqlQueryOutput)

    system_prompt_sql = f"""
IDENTITY: Expert Clinical SQL Architect.
TASK: Translate the user's English medical query into a read-only T-SQL statement.

DATABASE SCHEMA:
Table: patients (id, name, dob, gender, social_card, patient_id)
Table: medical_exams (exam_id, patient_id, exam_date, examination_type, source_url, diagnosis)

CONTEXT: 
Target Patient ID: {extracted_patient_id} 
Timeframe: {extracted_timeframe}
EXPANDED SEARCH TERMS: {query_en}

RULES:
1. Use ONLY `SELECT` statements. Do NOT use `TOP` or `LIMIT` clauses unless explicitly asked.
2. Join `patients` and `medical_exams` ON `patients.id = medical_exams.patient_id`.
3. FILTERING: Use the terms from EXPANDED SEARCH TERMS to filter the `diagnosis` or `examination_type` columns using `LOWER() LIKE '%term%'`. Apply 'OR' logic if multiple terms are present.
4. Select all relevant columns: name, patient_id, exam_date, examination_type, diagnosis, source_url.
"""

    logger.debug("Generating SQL based on expanded English query.")
    sql_data = structured_llm.invoke([
        ("system", system_prompt_sql),
        ("human", f"Build SQL for: {query_en}")
    ])

    generated_sql = sql_data.generated_sql
    db_results = []
    error_msg = None

    if not is_safe_sql(generated_sql):
        error_msg = "SECURITY_BLOCK: Attempted execution of a non-SELECT statement."
        logger.critical(f"Blocked unsafe SQL query: {generated_sql}")
    else:
        try:
            result_proxy = db.execute(text(generated_sql))
            db_results = [dict(row._mapping)
                          for row in result_proxy.fetchall()]
            logger.info(
                f"SQL execution successful. Retrieved {len(db_results)} rows.")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"SQL Execution Exception: {error_msg}")
        finally:
            db.close()

    if error_msg:
        return {
            "final_answer": f"⚠️ Տվյալների բազայի հետ կապված սխալ է առաջացել: `{error_msg}`",
            "next_node": "end"
        }

    return {
        "sql_results": db_results,
        "generated_sql": generated_sql,
        "next_node": "evaluator_agent"
    }
