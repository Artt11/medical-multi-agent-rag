# from typing import Dict, Any
# from sqlalchemy import text
# from src.core.config import llm
# from src.core.schemas import SqlQueryOutput
# from src.database.connection import SessionLocal
# from src.services.source_link_service import build_pdf_urls, format_source_links


# def temporal_disease_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("---TEMPORAL DISEASE AGENT (Agent 3) ---")

#     patient_id = state.get("patient_id")
#     original_query = state.get("query")
#     timeframe = state.get("timeframe") or "the specified time period"
#     disease_target = state.get("disease") or "any condition"

#     db = SessionLocal()

#     structured_llm = llm.with_structured_output(SqlQueryOutput)

#     patient_scope_rules = ""
#     patient_filter_rule = ""
#     patient_select_hint = ""

#     if patient_id:
#         patient_scope_rules = f"""
# MANDATORY PATIENT FILTER

# You are ONLY allowed to retrieve data for:

# patient_id = '{patient_id}'

# Every generated SQL query MUST include this condition.
# """
#         patient_filter_rule = "Always include the patient_id filter."
#         patient_select_hint = "Limit results to the specified patient."
#     else:
#         patient_scope_rules = """
# PATIENT SCOPE

# No specific patient_id was provided.
# Search across all patients and do NOT include a patient_id filter.
# """
#         patient_filter_rule = "Do not require a patient_id filter when it is missing."
#         patient_select_hint = "Include patient identifiers (patient_id and/or patient name) in SELECT when searching across all patients."

#     system_prompt = f"""
# ROLE
# You are a Clinical Temporal SQL Generation Agent.

# Your responsibility is to convert the user's medical question into a precise
# read-only SQL query that retrieves examination records within a defined timeframe.
# If a specific patient is provided, scope to that patient. Otherwise, search across all patients.

# --------------------------------------------------

# DATABASE SCHEMA

# Table: medical_exams
# Columns:
# - exam_date
# - diagnosis
# - patient_id
# - document_hash

# Table: patients
# Columns:
# - id
# - name

# Relationship:
# patients.id = medical_exams.patient_id

# --------------------------------------------------

# {patient_scope_rules}

# --------------------------------------------------

# TEMPORAL FILTERING

# Use the column:

# medical_exams.exam_date

# Apply SQL date filtering to match the requested timeframe.

# Example approaches may include:

# YEAR(exam_date)
# BETWEEN date ranges
# DATE comparisons

# --------------------------------------------------

# DIAGNOSIS MATCHING

# When filtering by disease use flexible matching:

# LOWER(medical_exams.diagnosis) LIKE '%{disease_target.lower()}%'

# --------------------------------------------------

# SELECT OUTPUT

# {patient_select_hint}
# Include medical_exams.document_hash in SELECT when available so source PDFs can be linked.

# --------------------------------------------------

# SECURITY RULES

# 1. Only generate SELECT queries
# 2. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE
# 3. Only reference the tables listed above
# 4. {patient_filter_rule}
# 5. Return only SQL code

# --------------------------------------------------

# OUTPUT FORMAT

# Return only the SQL query.
# No explanations.
# No markdown.
# """

#     sql_data = structured_llm.invoke([
#         ("system", system_prompt),
#         ("human",
#          f"Timeframe: {timeframe}. Disease: {disease_target}. User query: {original_query}")
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

#     patient_label = patient_id or "All patients"

#     if error_msg:

#         final_prompt = f"""
# ROLE
# You are a Clinical Data System Assistant.

# TASK
# Explain to the user that the temporal disease search for the patient
# could not be completed due to a database query failure.

# CONTEXT

# Patient: {patient_label}

# User Question:
# {original_query}

# Generated SQL:
# {generated_sql}

# Database Error:
# {error_msg}

# RULES

# - Do not speculate about technical causes.
# - Do not invent database schema details.
# - Do not fabricate patient medical data.
# - Provide a short professional explanation.

# OUTPUT
# A clear message informing the user that the temporal query failed.
# """

#     else:

#         final_prompt = f"""
# ROLE
# You are a Clinical Data Interpretation Assistant.

# TASK
# Summarize the temporal medical findings retrieved from the database.

# PATIENT
# {patient_label}

# SEARCH PARAMETERS
# Disease: {disease_target}
# Timeframe: {timeframe}

# DATABASE RESULTS
# {db_results}

# RULES

# 1. Use only the provided database results.
# 2. Do not invent diagnoses or examination records.
# 3. If the results list is empty, state that no matching records were found.
# 4. Use clear professional clinical language.

# OUTPUT STRUCTURE

# Temporal Disease Analysis

# Patient ID:
# {patient_id}

# Condition Searched:
# {disease_target}

# Timeframe:
# {timeframe}

# Number of Records Found:
# <count>

# Summary of Findings:
# <brief clinical interpretation>

# Records:
# <list records if present>
# """

#     final_response = llm.invoke([("system", final_prompt)])

#     doc_hashes = []
#     for row in db_results:
#         if not isinstance(row, dict):
#             continue
#         for key in ("document_hash", "doc_hash", "hash", "documentHash"):
#             value = row.get(key)
#             if value:
#                 doc_hashes.append(str(value))
#                 break

#     source_block = format_source_links(build_pdf_urls(doc_hashes))

#     return {
#         "final_answer": final_response.content + source_block,
#         "sql_results": db_results
#     }
from typing import Dict, Any
from sqlalchemy import text
from src.core.config import llm
from src.core.schemas import SqlQueryOutput
from src.database.connection import SessionLocal
# ՀԵՌԱՑՎԵԼ Է: source_link_service-ի ներմուծումը


def temporal_disease_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- ⏳ TEMPORAL DISEASE AGENT (Agent 3 - SQL Direct) ---")

    patient_id = state.get("patient_id")
    original_query = state.get("query")
    timeframe = state.get("timeframe") or "the specified time period"
    disease_target = state.get("disease") or "any condition"

    db = SessionLocal()
    structured_llm = llm.with_structured_output(SqlQueryOutput)

    # Պացիենտի ֆիլտրման կանոններ (Նույնն են մնում)
    patient_scope_rules = ""
    patient_filter_rule = ""
    patient_select_hint = ""

    if patient_id:
        patient_scope_rules = f"MANDATORY PATIENT FILTER: patient_id = '{patient_id}'"
        patient_filter_rule = "Always include the patient_id filter."
        patient_select_hint = "Limit results to the specified patient."
    else:
        patient_scope_rules = "PATIENT SCOPE: Search across all patients."
        patient_filter_rule = "Do not require a patient_id filter."
        patient_select_hint = "Include patient identifiers in SELECT."

    # Թարմացված System Prompt. Այստեղ ավելացրել ենք source_url-ը
    system_prompt = f"""
ROLE: Clinical Temporal SQL Generation Agent.

DATABASE SCHEMA
Table: medical_exams
Columns:
- exam_date
- diagnosis
- patient_id
- source_url      <-- ԱՎԵԼԱՑՎԱԾ Է
- document_hash

Table: patients
Columns:
- id
- name

{patient_scope_rules}

SELECT OUTPUT
{patient_select_hint}
IMPORTANT: Include medical_exams.source_url in SELECT so the user can access the original Google Drive document.

SECURITY: Return only SQL code. No markdown.
"""

    # SQL-ի գեներացում
    sql_data = structured_llm.invoke([
        ("system", system_prompt),
        ("human",
         f"Timeframe: {timeframe}. Disease: {disease_target}. Query: {original_query}")
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

    # Արդյունքների ամփոփում LLM-ով
    if error_msg:
        final_prompt = f"Explain that the query failed: {error_msg}"
    else:
        final_prompt = f"""
        Summarize these temporal medical findings:
        Patient: {patient_id or 'All'}
        Disease: {disease_target}
        Timeframe: {timeframe}
        Results: {db_results}
        """

    final_response = llm.invoke([("system", final_prompt)])

    # Հղումների հավաքագրում (Այլևս չենք կառուցում հաշերով, վերցնում ենք URL-ը)
    source_urls = set()
    for row in db_results:
        url = row.get("source_url") or row.get("sourceUrl")
        if url:
            source_urls.add(str(url))

    # Հղումների բլոկի ձևավորում
    source_block = ""
    if source_urls:
        source_block = "\n\n🔗 **Source Documents (Google Drive):**\n" + "\n".join(
            [f"- [Դիտել Ֆայլը]({url})" for url in source_urls]
        )

    return {
        "final_answer": final_response.content + source_block,
        "sql_results": db_results
    }
