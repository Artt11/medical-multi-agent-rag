from typing import Dict, Any
import json
from sqlalchemy import text
from src.core.config import llm
from src.database.connection import SessionLocal
from src.services.source_link_service import build_pdf_urls, format_source_links


def statistical_filter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("---STATISTICAL FILTER AGENT (Agent 7) ---")

    db = SessionLocal()

    system_prompt = """
ROLE
You are a Clinical Data Science SQL Agent.

Your task is to convert the user's statistical medical query into a precise,
read-only T-SQL query.

--------------------------------------------------

DATABASE SCHEMA

Table: patients
Columns:
- id
- name
- dob
- gender
- social_card

Table: medical_exams
Columns:
- exam_id
- patient_id
- exam_date
- diagnosis
- conclusion
- recommendations
- examination_type
- document_hash

Relationship:
patients.id = medical_exams.patient_id

--------------------------------------------------

TASK

Generate a SQL query that retrieves patient cohorts or medical exam data
based on statistical filters requested by the user.

These may include:

• age filtering (derived from dob)
• name-based patient lookup
• birth year filtering (e.g., "born in 2000")
• diagnosis-based filtering
• examination date ranges
• cohort counting or grouping
• patient analysis or results by name

--------------------------------------------------

SECURITY RULES

1. READ-ONLY DATABASE ACCESS
Only generate SELECT queries.

Never generate:
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE

2. SCHEMA CONSTRAINT
Use ONLY the tables and columns defined above.

3. JOIN RULE
If both patient and exam data are needed, join tables using:

patients.id = medical_exams.patient_id

4. DIAGNOSIS MATCHING
When filtering diagnoses, use flexible matching:

LOWER(medical_exams.diagnosis) LIKE '%keyword%'

5. NAME MATCHING
When filtering by patient name, use flexible matching:

LOWER(patients.name) LIKE '%name%'

6. BIRTH YEAR FILTERING
When filtering by birth year, use:

YEAR(patients.dob) = <year>

7. PATIENT ANALYSIS QUERIES
If the user asks for a specific patient's medical analysis or results by name,
select patient identity plus exam details. Include at least:

patients.name, patients.dob, patients.gender,
medical_exams.exam_date, medical_exams.examination_type,
medical_exams.diagnosis, medical_exams.conclusion, medical_exams.recommendations,
medical_exams.document_hash

8. OUTPUT FORMAT
Return ONLY the SQL query.
No explanations.
No markdown.
"""

    sql_response = llm.invoke([
        ("system", system_prompt),
        ("human", state["query"])
    ])

    generated_sql = sql_response.content.replace(
        "```sql", "").replace("```", "").strip()

    print(f"Generated SQL: {generated_sql}")

    db_results = []
    error_msg = None

    try:
        result_proxy = db.execute(text(generated_sql))
        db_results = [dict(row._mapping) for row in result_proxy.fetchall()]
    except Exception as e:
        error_msg = str(e)
        print(f"SQL Error: {error_msg}")
    finally:
        db.close()

    if error_msg:
        explanation_prompt = f"""
ROLE
You are a Healthcare Data System Assistant.

TASK
Explain to the user that their statistical medical query could not be completed.

CONTEXT
Generated SQL:
{generated_sql}

Database Error:
{error_msg}

RULES
- Do not speculate about technical causes.
- Do not invent database schema information.
- Provide a short and professional explanation.

OUTPUT
A clear message explaining that the statistical analysis could not be executed.
"""

    else:
        explanation_prompt = f"""
ROLE
You are a Clinical Data Analyst.

TASK
Explain the results retrieved from the medical database.

USER QUESTION
{state['query']}

DATABASE RESULTS
{db_results}

RULES
1. Use only the provided database results.
2. Do not invent additional patient data.
3. Do not display raw JSON or dictionary structures.
4. Choose the output format based on the query type:
   - If the user asks for specific patients by name or DOB, return a patient list.
   - Otherwise, summarize the statistical findings.

OUTPUT STRUCTURE (Patient Lookup)

Patient Search Result

Query Summary:
<brief description>

Number of Patients:
<count>

Patient Records:
<list of patients and key fields>

OUTPUT STRUCTURE (Patient Analysis)

Patient Medical Analysis

Query Summary:
<brief description>

Number of Records:
<count>

Records:
<per-exam analysis using diagnosis/conclusion/recommendations>

OUTPUT STRUCTURE (Statistical)

Statistical Analysis Result

Query Summary:
<brief description of the analysis>

Number of Records:
<count>

Key Findings:
<short interpretation of the data>
"""

    def normalize_value(value: Any) -> str:
        if value is None:
            return "Not provided"
        if isinstance(value, (list, tuple)):
            items = [normalize_value(v) for v in value if v is not None]
            return "; ".join([v for v in items if v and v != "Not provided"]) or "Not provided"
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return "Not provided"
            if (raw.startswith("{") and raw.endswith("}")) or (raw.startswith("[") and raw.endswith("]")):
                try:
                    parsed = json.loads(raw)
                    return normalize_value(parsed)
                except Exception:
                    return raw
            return raw
        return str(value)

    def is_analysis_query(query_text: str) -> bool:
        if not query_text:
            return False
        lowered = query_text.lower()
        keywords = (
            "analysis",
            "result",
            "results",
            "report",
            "condition",
            "diagnosis",
            "conclusion",
            "recommendation",
            "exam",
            "test",
        )
        return any(k in lowered for k in keywords)

    if not error_msg and db_results and is_analysis_query(state.get("query", "")):
        lines = [
            "Patient Medical Analysis",
            "",
            f"Query Summary: {state.get('query')}",
            f"Number of Records: {len(db_results)}",
            "",
        ]

        for idx, row in enumerate(db_results, start=1):
            if not isinstance(row, dict):
                continue
            lines.append(f"Record {idx}:")
            lines.append(f"Exam Date: {normalize_value(row.get('exam_date'))}")
            lines.append(
                f"Examination Type: {normalize_value(row.get('examination_type'))}")
            lines.append(f"Diagnosis: {normalize_value(row.get('diagnosis'))}")
            lines.append(
                f"Conclusion: {normalize_value(row.get('conclusion'))}")
            lines.append(
                f"Recommendations: {normalize_value(row.get('recommendations'))}")
            lines.append("")

        final_text = "\n".join(lines).strip()
    else:
        final_response = llm.invoke([("system", explanation_prompt)])
        final_text = final_response.content

    doc_hashes = []
    for row in db_results:
        if not isinstance(row, dict):
            continue
        for key in ("document_hash", "doc_hash", "hash", "documentHash"):
            value = row.get(key)
            if value:
                doc_hashes.append(str(value))
                break

    source_block = format_source_links(build_pdf_urls(doc_hashes))

    return {
        "final_answer": final_text + source_block,
        "sql_results": db_results
    }
