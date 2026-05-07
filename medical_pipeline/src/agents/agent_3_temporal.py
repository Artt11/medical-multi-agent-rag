# from typing import Dict, Any
# from sqlalchemy import text
# from src.core.config import llm
# from src.core.schemas import SqlQueryOutput
# from src.database.connection import SessionLocal


# def temporal_disease_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     # print("--- ⏳ TEMPORAL DISEASE AGENT (Agent 3 - Optimized) ---")

#     patient_id = state.get("patient_id")
#     original_query = state.get("query", "")
#     timeframe = state.get("timeframe") or "the specified time period"
#     disease_target = state.get("disease") or "any condition"

#     db = SessionLocal()
#     structured_llm = llm.with_structured_output(SqlQueryOutput)

#     if patient_id:
#         patient_scope_rules = f"MANDATORY FILTER: You MUST include `medical_exams.patient_id = '{patient_id}'` in the WHERE clause."
#         patient_select_hint = "Select only medical exam details (date, diagnosis, url)."
#     else:
#         patient_scope_rules = "SCOPE: Search across ALL patients. Do not filter by patient_id."
#         patient_select_hint = "Select patient names along with medical exam details."

#     system_prompt = f"""
# ROLE: You are an Expert Clinical Temporal SQL Engineer.

# TASK: Write a highly precise, read-only SQL query to retrieve medical records based on a specific disease and timeframe.

# <schema>
# Table: patients
# Columns:
# - id (INT, Primary Key)
# - name (VARCHAR)

# Table: medical_exams
# Columns:
# - patient_id (INT, Foreign Key to patients.id)
# - exam_date (DATE)
# - diagnosis (VARCHAR)
# - source_url (VARCHAR)
# </schema>

# <rules>
# 1. READ-ONLY: ONLY use `SELECT` statements.
# 2. JOINS: Join `patients.id = medical_exams.patient_id` when searching across all patients.
# 3. DISEASE MATCHING: Use case-insensitive matching: `LOWER(medical_exams.diagnosis) LIKE '%<keyword>%'`.
# 4. TEMPORAL FILTERING: Convert the human timeframe ('{timeframe}') into valid SQL date comparisons (e.g., `exam_date >= '2023-01-01'`, or `exam_date >= DATEADD(month, -6, GETDATE())`).
# 5. OUTPUT: Return strictly the raw SQL. No markdown, no explanations.
# 6. SOURCE URL: ALWAYS include `medical_exams.source_url` in your SELECT statement.
# 7. {patient_scope_rules}
# </rules>

# SELECT HINT: {patient_select_hint}
# """

#     sql_data = structured_llm.invoke([
#         ("system", system_prompt),
#         ("human",
#          f"Timeframe: {timeframe} | Disease: {disease_target} | Query: {original_query}")
#     ])

#     generated_sql = sql_data.generated_sql
#     db_results = []
#     error_msg = None

#     try:
#         result_proxy = db.execute(text(generated_sql))
#         db_results = [dict(row._mapping) for row in result_proxy.fetchall()]
#     except Exception as e:
#         error_msg = str(e)
#         print(f"--- ⚠️ SQL Execution Error: {error_msg} ---")
#     finally:
#         db.close()

#     patient_label = patient_id or "All patients (Ամբողջ բազան)"

#     if error_msg:
#         final_prompt = f"""
# ROLE: Clinical System Assistant
# TASK: Inform the user that the temporal query failed due to a database error.
# CONTEXT: Error - {error_msg}
# RULES: Be professional, do not show the raw SQL. Suggest rephrasing the date or timeframe. Respond in Armenian.
# """
#     else:
#         final_prompt = f"""
# ROLE: Clinical Data Interpretation Assistant

# TASK: Summarize the temporal medical findings.

# <data>
# Patient Scope: {patient_label}
# Target Disease: {disease_target}
# Timeframe: {timeframe}
# Total Records Found: {len(db_results)}
# Results: {db_results}
# </data>

# RULES:
# 1. STRICT GROUNDING: Use ONLY the data provided above.
# 2. EMPTY STATE: If Total Records Found is 0, state clearly that no records were found for this timeframe and disease.
# 3. LANGUAGE: Generate the final response in Armenian.
# 4. STRUCTURE: Use clear markdown with clinical professionalism.

# OUTPUT FORMAT:
# ### ⏳ Ժամանակագրական որոնման արդյունքներ

# **Պացիենտ:** {patient_label}
# **Ախտորոշում:** {disease_target}
# **Ժամանակահատված:** {timeframe}
# **Գտնված գրառումներ:** {len(db_results)}

# **Ամփոփում:**
# <Հակիրճ նկարագրություն ըստ գտնված տվյալների (եթե կան)>

# **Ժամանակագրություն (Timeline):**
# <List format: Date - Diagnosis - Patient Name (if applicable)> (Բաց թողնել, եթե 0 է)
# """

#     final_response = llm.invoke([
#         ("system", final_prompt),
#         ("human", f"User Query: {original_query}")
#     ])

#     source_urls = set()
#     for row in db_results:
#         url = row.get("source_url") or row.get("sourceUrl")
#         if url:
#             source_urls.add(str(url))

#     source_block = ""
#     if source_urls:
#         source_block = "\n\n🔗 **Կից փաստաթղթեր (Google Drive):**\n" + "\n".join(
#             [f"- [Դիտել Ֆայլը]({url})" for url in source_urls]
#         )

#     return {
#         "final_answer": final_response.content + source_block,
#         "sql_results": db_results,
#         "generated_sql": generated_sql
#     }
