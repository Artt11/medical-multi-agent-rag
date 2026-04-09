# from typing import Dict, Any
# from sqlalchemy import text
# from src.core.config import llm
# from src.core.schemas import SqlQueryOutput
# from src.database.connection import SessionLocal


# def disease_cohort_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("---DISEASE COHORT AGENT (Agent 2) ---")

#     db = SessionLocal()
#     disease_target = state.get("disease") or "the specified condition"

#     structured_llm = llm.with_structured_output(SqlQueryOutput)

#     system_prompt = """
# ROLE
# You are a Clinical SQL Generation Agent responsible for translating medical questions into safe read-only T-SQL queries.

# TASK
# Convert the user's request into a precise SQL SELECT query that retrieves patients with the requested disease or condition.

# --------------------------------------------------

# DATABASE SCHEMA

# Table: patients
# Columns:
# - id
# - name
# - dob
# - gender

# Table: medical_exams
# Columns:
# - patient_id
# - diagnosis
# - conclusion

# Relationship:
# patients.id = medical_exams.patient_id

# --------------------------------------------------

# STRICT RULES

# 1. READ-ONLY DATABASE ACCESS
# Only generate SELECT statements.

# Never generate:
# INSERT
# UPDATE
# DELETE
# DROP
# ALTER
# TRUNCATE

# 2. USE ONLY PROVIDED TABLES
# You may only reference:
# patients
# medical_exams

# Do not invent tables or columns.

# 3. DIAGNOSIS MATCHING
# Diagnoses may contain additional words or case differences.

# Always filter using:

# LOWER(medical_exams.diagnosis) LIKE '%<disease_keyword>%'

# Never use exact equality.

# 4. TABLE JOINS
# When patient information and diagnosis data are needed, join tables using:

# patients.id = medical_exams.patient_id

# 5. OUTPUT FORMAT
# Return ONLY the SQL query.
# No explanations.
# No markdown.
# No comments.

# 6. INVALID REQUESTS
# If the request cannot be mapped to the schema, return exactly:

# SELECT NULL WHERE 1=0;

# --------------------------------------------------

# EXAMPLE

# SELECT p.name, p.gender, m.diagnosis, m.conclusion
# FROM patients p
# JOIN medical_exams m ON p.id = m.patient_id
# WHERE LOWER(m.diagnosis) LIKE '%pneumonia%';
# """

#     sql_data = structured_llm.invoke([
#         ("system", system_prompt),
#         ("human",
#          f"Find patients with: {disease_target}. User query: {state['query']}")
#     ])

#     generated_sql = sql_data.generated_sql
#     db_results = []
#     error_msg = None

#     try:
#         result_proxy = db.execute(text(generated_sql))
#         db_results = [dict(row._mapping) for row in result_proxy.fetchall()]
#     except Exception as e:
#         error_msg = str(e)
#         print(f"SQL Execution Error: {error_msg}")
#     finally:
#         db.close()

#     if error_msg:
#         final_prompt = f"""
# ROLE
# You are a clinical system assistant.

# TASK
# Explain to the user that their disease search could not be completed due to a database query failure.

# CONTEXT
# Generated SQL:
# {generated_sql}

# Database Error:
# {error_msg}

# RULES
# - Do not speculate about unknown technical causes.
# - Do not invent database schema details.
# - Explain the failure clearly and professionally.
# - Suggest the user try rephrasing the request.

# OUTPUT
# A short professional explanation for the user.
# """
#     else:
#         final_prompt = f"""
# ROLE
# You are a Clinical Data Interpretation Assistant.

# TASK
# Summarize the database results of a disease cohort search.

# SEARCH TARGET
# {disease_target}

# DATABASE RESULTS
# {db_results}

# RULES
# 1. Use only the provided database results.
# 2. Do not invent patient records or diagnoses.
# 3. If the results list is empty, clearly state that no patients match the criteria.
# 4. Use professional clinical language.

# OUTPUT STRUCTURE

# Cohort Search Result

# Target Condition:
# {disease_target}

# Number of Patients Found:
# <count>

# Summary:
# <brief description of findings>

# Patient Records:
# <list of patients if present>
# """

#     final_response = llm.invoke([
#         ("system", final_prompt)
#     ])

#     return {
#         "final_answer": final_response.content,
#         "sql_results": db_results
#     }
from typing import Dict, Any
from sqlalchemy import text
from src.core.config import llm
from src.core.schemas import SqlQueryOutput
from src.database.connection import SessionLocal


def disease_cohort_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- 📊 DISEASE COHORT AGENT (Agent 2 - Optimized) ---")

    db = SessionLocal()
    disease_target = state.get("disease") or "the specified condition"
    user_query = state.get("query", "")

    structured_llm = llm.with_structured_output(SqlQueryOutput)

    # ==========================================
    # 1. OPTIMIZED SQL GENERATION PROMPT
    # ==========================================
    system_prompt = """
ROLE:
You are an Expert Clinical SQL Engineer. Your task is to translate user requests into precise, read-only T-SQL queries.

<schema>
Table: patients
Columns:
- id (INT, Primary Key)
- name (VARCHAR)
- dob (DATE)
- gender (VARCHAR)

Table: medical_exams
Columns:
- patient_id (INT, Foreign Key to patients.id)
- diagnosis (VARCHAR)
- conclusion (VARCHAR)
</schema>

STRICT RULES:
1. READ-ONLY ACCESS: Use ONLY `SELECT` statements. NO modifications (INSERT/UPDATE/DELETE).
2. SCHEMA LOCK: Only use the tables and columns provided in the <schema> block. Do not hallucinate columns.
3. PREVENT DUPLICATES: Always use `SELECT DISTINCT` when retrieving patient data to avoid duplicate rows for the same patient.
4. ROBUST MATCHING: Use case-insensitive matching for diagnoses. Example: `LOWER(medical_exams.diagnosis) LIKE '%<keyword>%'`.
5. JOINS: Join strictly on `patients.id = medical_exams.patient_id`.
6. OUTPUT: Return ONLY the raw SQL string. Do not include markdown formatting (like ```sql), prefixes, or comments.

EXAMPLE:
User: Find female patients with pneumonia
Target Disease: pneumonia
SQL Output: SELECT DISTINCT p.name, p.gender, m.diagnosis FROM patients p JOIN medical_exams m ON p.id = m.patient_id WHERE p.gender = 'F' AND LOWER(m.diagnosis) LIKE '%pneumonia%';
"""

    sql_data = structured_llm.invoke([
        ("system", system_prompt),
        ("human",
         f"Target Disease: {disease_target}\nUser Query: {user_query}")
    ])

    generated_sql = sql_data.generated_sql
    db_results = []
    error_msg = None

    try:
        result_proxy = db.execute(text(generated_sql))
        db_results = [dict(row._mapping) for row in result_proxy.fetchall()]
    except Exception as e:
        error_msg = str(e)
        print(f"--- ⚠️ SQL Execution Error: {error_msg} ---")
    finally:
        db.close()

    # ==========================================
    # 2. OPTIMIZED INTERPRETATION PROMPT
    # ==========================================
    if error_msg:
        final_prompt = f"""
ROLE: Clinical System Assistant

TASK: Inform the user that the database search failed due to a technical error.

<context>
Generated SQL: {generated_sql}
Error: {error_msg}
</context>

RULES:
- Do not expose raw SQL or technical error messages to the user.
- Explain the failure professionally and empatheticly.
- Suggest rephrasing the request.
- Respond in the language of the user's original query (Armenian if requested in Armenian).
"""
    else:
        final_prompt = f"""
ROLE: Clinical Data Interpretation Assistant

TASK: Summarize the results of a patient cohort search.

<data>
Target Condition: {disease_target}
Total Patients Found: {len(db_results)}
Database Results: {db_results}
</data>

RULES:
1. STRICT GROUNDING: Use ONLY the data provided in the <data> tags. Do not invent names, records, or diagnoses.
2. EMPTY RESULTS HANDLING: If "Total Patients Found" is 0, explicitly and clearly state that no patients matched the criteria. Do not attempt to summarize non-existent data.
3. LANGUAGE: Generate your response in Armenian (unless the user query dictates otherwise).
4. PROFESSIONAL TONE: Use clinical, professional language.

OUTPUT STRUCTURE:
### 📊 Որոնման արդյունքներ (Cohort Search)

**Թիրախային ախտորոշում:** {disease_target}
**Գտնված պացիենտների քանակ:** <count>

**Ամփոփում:**
<Հակիրճ նկարագրություն գտնված տվյալների հիման վրա>

**Պացիենտների ցանկ:**
<List format: Name - Gender - Diagnosis. (Եթե քանակը 0 է, բաց թող այս բաժինը)>
"""

    final_response = llm.invoke([
        ("system", final_prompt),
        ("human", f"User Original Query: {user_query}")
    ])

    return {
        "final_answer": final_response.content,
        "sql_results": db_results,
        "generated_sql": generated_sql  # Ավելացրել եմ, որ դու կարողանաս debug անել
    }
