import operator
from typing import Annotated, List, TypedDict, Optional, Any, Dict


class AgentState(TypedDict):
    query: str
    english_query: str
    user_language: str

    next_node: str

    patient_id: Optional[str]
    patient_internal_id: Optional[int]
    timeframe: Optional[str]
    disease: Optional[str]

    intermediate_steps: Annotated[List[str], operator.add]

    context_chunks: Annotated[List[str], operator.add]
    sql_results: Annotated[List[Dict[str, Any]], operator.add]

    needs_pdf: bool
    attachment_path: Optional[str]
    attachment_name: Optional[str]

    final_answer: str
