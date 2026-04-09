
# from typing import Dict, Any
# import json
# from sqlalchemy import text
# from src.core.config import llm
# from src.database.connection import SessionLocal
# # ՀԵՌԱՑՎԵԼ Է: source_link_service-ի ներմուծումը


# def statistical_filter_node(state: Dict[str, Any]) -> Dict[str, Any]:
#     print("--- 📊 STATISTICAL FILTER AGENT (Agent 7 - SQL Direct) ---")

#     db = SessionLocal()

#     system_prompt = """
# ROLE
# You are a Clinical Data Science SQL Agent.
# Your task is to convert the user's statistical medical query into a precise T-SQL query.

# --------------------------------------------------
# DATABASE SCHEMA

# Table: patients
# Columns: [id, name, dob, gender, social_card]

# Table: medical_exams
# Columns:
# - exam_id, patient_id, exam_date, examination_type
# - diagnosis, conclusion, recommendations
# - document_hash
# - source_url      <-- ԱՎԵԼԱՑՎԱԾ Է (Google Drive URL)

# Relationship: patients.id = medical_exams.patient_id
# --------------------------------------------------

# TASK
# Generate a SQL query to retrieve patient cohorts or medical exam data.

# IMPORTANT:
# If the user asks for a specific patient's medical analysis or results,
# ALWAYS include 'medical_exams.source_url' in your SELECT statement
# so we can provide the original document link.

# SECURITY: Return ONLY the SQL query. No markdown.
# """

#     sql_response = llm.invoke([
#         ("system", system_prompt),
#         ("human", state["query"])
#     ])

#     generated_sql = sql_response.content.replace(
#         "```sql", "").replace("```", "").strip()
#     print(f"Generated SQL: {generated_sql}")

#     db_results = []
#     error_msg = None

#     try:
#         result_proxy = db.execute(text(generated_sql))
#         db_results = [dict(row._mapping) for row in result_proxy.fetchall()]
#     except Exception as e:
#         error_msg = str(e)
#         print(f"SQL Error: {error_msg}")
#     finally:
#         db.close()

#     # Արդյունքների բացատրության լոգիկան (Նույնն է մնում, ինչ քո կոդում)
#     if error_msg:
#         explanation_prompt = f"Explain SQL error: {error_msg}"
#     else:
#         explanation_prompt = f"Summarize these clinical results for query '{state['query']}': {db_results}"

#     # ... (normalize_value և is_analysis_query ֆունկցիաները պահվում են անփոփոխ) ...
#     # (Այստեղ ես կրճատում եմ տեքստը, բայց քո ֆայլում պահիր դրանք)

#     final_response = llm.invoke([("system", explanation_prompt)])
#     final_text = final_response.content

#     # Հղումների հավաքագրում (Այլևս չենք կանչում build_pdf_urls)
#     source_urls = set()
#     for row in db_results:
#         if not isinstance(row, dict):
#             continue
#         # Վերցնում ենք URL-ը ուղիղ SQL-ի արդյունքից
#         url = row.get("source_url") or row.get("sourceUrl")
#         if url:
#             source_urls.add(str(url))

#     # Ձևավորում ենք հղումների բլոկը
#     source_block = ""
#     if source_urls:
#         source_block = "\n\n🔗 **Source Documents (Google Drive):**\n" + "\n".join(
#             [f"- [Դիտել Ֆայլը]({url})" for url in source_urls]
#         )

#     return {
#         "final_answer": final_text + source_block,
#         "sql_results": db_results
#     }
from typing import Dict, Any
from sqlalchemy import text
from src.core.config import llm
# Վերադարձրել ենք անվտանգության համար
from src.core.schemas import SqlQueryOutput
from src.database.connection import SessionLocal


def statistical_filter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- 📊 STATISTICAL FILTER AGENT (Agent 7 - Optimized) ---")

    db = SessionLocal()
    user_query = state.get("query", "")

    # Օգտագործում ենք Structured Output վստահելի SQL ստանալու համար
    structured_llm = llm.with_structured_output(SqlQueryOutput)

    # ==========================================
    # 1. OPTIMIZED SQL GENERATION PROMPT
    # ==========================================
    system_prompt = """
ROLE: You are an Expert Clinical Data Scientist & SQL Architect.
TASK: Translate the user's statistical or cohort-based medical query into an optimized, read-only T-SQL query.

<schema>
Table: patients
Columns:
- id (INT, Primary Key)
- name (VARCHAR)
- dob (DATE)
- gender (VARCHAR)
- social_card (VARCHAR)

Table: medical_exams
Columns: 
- exam_id (INT, Primary Key)
- patient_id (INT, Foreign Key to patients.id)
- exam_date (DATE)
- examination_type (VARCHAR)
- diagnosis (VARCHAR)
- conclusion (VARCHAR)
- recommendations (VARCHAR)
- source_url (VARCHAR)
</schema>

<rules>
1. READ-ONLY: Use ONLY `SELECT` statements. NO modifications.
2. AGGREGATION VS RECORDS: 
   - If the query asks for statistics (counts, averages, percentages), use `COUNT()`, `GROUP BY`, etc. Do NOT select `source_url` for grouped/counted queries.
   - If the query asks for a list of specific patients/exams, ALWAYS include `medical_exams.source_url`.
3. JOINS: Join `patients.id = medical_exams.patient_id` when both demographic and exam data are needed.
4. TEXT MATCHING: Use `LOWER(column) LIKE '%keyword%'` for text searches.
5. OUTPUT FORMAT: Return ONLY the raw SQL query. No markdown, no explanations.
</rules>
"""

    sql_data = structured_llm.invoke([
        ("system", system_prompt),
        ("human", f"User Query: {user_query}")
    ])

    generated_sql = sql_data.generated_sql
    print(f"--- ⚡ Generated SQL: {generated_sql} ---")

    db_results = []
    error_msg = None

    try:
        result_proxy = db.execute(text(generated_sql))
        db_results = [dict(row._mapping) for row in result_proxy.fetchall()]
    except Exception as e:
        error_msg = str(e)
        print(f"--- ⚠️ SQL Error: {error_msg} ---")
    finally:
        db.close()

    # ==========================================
    # 2. OPTIMIZED INTERPRETATION PROMPT
    # ==========================================
    if error_msg:
        explanation_prompt = f"""
ROLE: Clinical Data Analyst
TASK: Inform the user about a statistical query failure.
CONTEXT: Error: {error_msg}
RULES: Do not expose raw SQL. Explain the failure professionally in Armenian.
"""
    else:
        explanation_prompt = f"""
ROLE: Clinical Data Analyst
TASK: Present the statistical and clinical results clearly.

<data>
User Query: {user_query}
Database Results: {db_results}
</data>

<rules>
1. STRICT GROUNDING: Use ONLY the provided Database Results.
2. EMPTY STATE: If Database Results is `[]`, state clearly: "Տվյալների բազայում համապատասխան վիճակագրություն կամ գրառումներ չեն գտնվել:"
3. FORMATTING: Present the data using a Markdown Table (if tabular data) or structured bullet points (if counts/statistics).
4. LANGUAGE: Generate the final summary strictly in Armenian.
5. PROFESSIONAL TONE: Provide a brief analytical conclusion based on the numbers.
</rules>

OUTPUT FORMAT:
### 📊 Վիճակագրական և Տվյալների Վերլուծություն
**Ամփոփում:** <Հակիրճ վերլուծություն>
**Արդյունքներ:** <Աղյուսակ կամ ցանկ>
"""

    final_response = llm.invoke([
        ("system", explanation_prompt),
        ("human", "Generate the statistical report.")
    ])

    final_text = final_response.content

    # ==========================================
    # 3. SOURCE URL HANDLING
    # ==========================================
    source_urls = set()
    for row in db_results:
        if not isinstance(row, dict):
            continue
        # Վերցնում ենք URL-ը (ապահովագրված case-sensitivity-ից)
        url = row.get("source_url") or row.get("sourceUrl")
        if url:
            source_urls.add(str(url))

    source_block = ""
    if source_urls:
        source_block = "\n\n🔗 **Կից փաստաթղթեր (Google Drive):**\n" + "\n".join(
            [f"- [Դիտել Ֆայլը]({url})" for url in source_urls]
        )

    return {
        "final_answer": final_text + source_block,
        "sql_results": db_results,
        "generated_sql": generated_sql
    }
