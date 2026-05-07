import re
from typing import Dict, Any
from sqlalchemy import text
from src.core.config import llm
from src.core.schemas import SqlQueryOutput
from src.database.connection import SessionLocal
from src.utils.logger import get_logger
from src.agents.state import AgentState

logger = get_logger("COHORT_AGENT")


def is_safe_sql(sql_query: str) -> bool:
    forbidden_pattern = re.compile(
        r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|EXEC|MERGE|GRANT|REVOKE)\b',
        re.IGNORECASE
    )
    return not bool(forbidden_pattern.search(sql_query))


def disease_cohort_node(state: AgentState) -> Dict[str, Any]:
    logger.info("--- 📊 DISEASE COHORT AGENT (SQL-Based Fetching) ---")

    db = SessionLocal()
    query_en = state.get("english_query", state.get("query", ""))

    steps = []

    structured_llm = llm.with_structured_output(SqlQueryOutput)

    sql_system_prompt = f"""
ROLE: Expert Clinical SQL Engineer.
TASK: Translate patient list requests into read-only T-SQL queries.
(Schema and Rules remain the same...)
"""

    db_results = []
    try:
        sql_response = structured_llm.invoke([
            ("system", sql_system_prompt),
            ("human", f"Generate SQL for this expanded query: {query_en}")
        ])

        generated_sql = sql_response.generated_sql
        logger.info(f"Generated SQL: {generated_sql}")

        if not is_safe_sql(generated_sql):
            logger.critical(f"Blocked unsafe SQL: {generated_sql}")
            return {
                "final_answer": "⚠️ Անվտանգության համակարգը բլոկավորեց SQL հարցումը:",
                "next_node": "end",
                "intermediate_steps": ["⚠️ **SQL Գործակալ**: Անվտանգության արգելափակում: Հայտնաբերվել է արգելված SQL հրահանգ:"]
            }

        result_proxy = db.execute(text(generated_sql))
        db_results = [dict(row._mapping) for row in result_proxy.fetchall()]

        steps.append(
            f"📊 **SQL Գործակալ**: Գեներացվեց հարցում և բազայից հաջողությամբ դուրս բերվեց **{len(db_results)}** գրառում:")

    except Exception as e:
        logger.error(f"SQL Execution Error: {e}")
        return {
            "final_answer": "Սխալ՝ տվյալների բազայի հետ կապ հաստատելիս:",
            "next_node": "end",
            "intermediate_steps": [f"❌ **SQL Գործակալ**: Տեղի է ունեցել տեխնիկական սխալ հարցման կատարման ժամանակ:"]
        }
    finally:
        db.close()

    return {
        "sql_results": db_results,
        "next_node": "evaluator_agent",
        "intermediate_steps": steps
    }
