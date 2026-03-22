from typing import Dict, Any
from sqlalchemy import text
from src.core.config import llm
from src.core.schemas import SqlQueryOutput
from src.database.connection import SessionLocal


def disease_cohort_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("---DISEASE COHORT AGENT (Agent 2) ---")

    db = SessionLocal()
    disease_target = state.get("disease") or "the specified condition"

    structured_llm = llm.with_structured_output(SqlQueryOutput)

    system_prompt = """
ROLE
You are a Clinical SQL Generation Agent responsible for translating medical questions into safe read-only T-SQL queries.

TASK
Convert the user's request into a precise SQL SELECT query that retrieves patients with the requested disease or condition.

--------------------------------------------------

DATABASE SCHEMA

Table: patients
Columns:
- id
- name
- dob
- gender

Table: medical_exams
Columns:
- patient_id
- diagnosis
- conclusion

Relationship:
patients.id = medical_exams.patient_id

--------------------------------------------------

STRICT RULES

1. READ-ONLY DATABASE ACCESS
Only generate SELECT statements.

Never generate:
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE

2. USE ONLY PROVIDED TABLES
You may only reference:
patients
medical_exams

Do not invent tables or columns.

3. DIAGNOSIS MATCHING
Diagnoses may contain additional words or case differences.

Always filter using:

LOWER(medical_exams.diagnosis) LIKE '%<disease_keyword>%'

Never use exact equality.

4. TABLE JOINS
When patient information and diagnosis data are needed, join tables using:

patients.id = medical_exams.patient_id

5. OUTPUT FORMAT
Return ONLY the SQL query.
No explanations.
No markdown.
No comments.

6. INVALID REQUESTS
If the request cannot be mapped to the schema, return exactly:

SELECT NULL WHERE 1=0;

--------------------------------------------------

EXAMPLE

SELECT p.name, p.gender, m.diagnosis, m.conclusion
FROM patients p
JOIN medical_exams m ON p.id = m.patient_id
WHERE LOWER(m.diagnosis) LIKE '%pneumonia%';
"""

    sql_data = structured_llm.invoke([
        ("system", system_prompt),
        ("human",
         f"Find patients with: {disease_target}. User query: {state['query']}")
    ])

    generated_sql = sql_data.generated_sql
    db_results = []
    error_msg = None

    try:
        result_proxy = db.execute(text(generated_sql))
        db_results = [dict(row._mapping) for row in result_proxy.fetchall()]
    except Exception as e:
        error_msg = str(e)
        print(f"SQL Execution Error: {error_msg}")
    finally:
        db.close()

    if error_msg:
        final_prompt = f"""
ROLE
You are a clinical system assistant.

TASK
Explain to the user that their disease search could not be completed due to a database query failure.

CONTEXT
Generated SQL:
{generated_sql}

Database Error:
{error_msg}

RULES
- Do not speculate about unknown technical causes.
- Do not invent database schema details.
- Explain the failure clearly and professionally.
- Suggest the user try rephrasing the request.

OUTPUT
A short professional explanation for the user.
"""
    else:
        final_prompt = f"""
ROLE
You are a Clinical Data Interpretation Assistant.

TASK
Summarize the database results of a disease cohort search.

SEARCH TARGET
{disease_target}

DATABASE RESULTS
{db_results}

RULES
1. Use only the provided database results.
2. Do not invent patient records or diagnoses.
3. If the results list is empty, clearly state that no patients match the criteria.
4. Use professional clinical language.

OUTPUT STRUCTURE

Cohort Search Result

Target Condition:
{disease_target}

Number of Patients Found:
<count>

Summary:
<brief description of findings>

Patient Records:
<list of patients if present>
"""

    final_response = llm.invoke([
        ("system", final_prompt)
    ])

    return {
        "final_answer": final_response.content,
        "sql_results": db_results
    }
