from typing import Annotated, List, TypedDict, Optional, Any, Dict
import operator


class AgentState(TypedDict):
    query: str

    next_node: str
    patient_id: Optional[str]
    patient_internal_id: Optional[int]

    timeframe: Optional[str]
    disease: Optional[str]

    context_chunks: Annotated[List[str], operator.add]
    sql_results: Annotated[List[Dict[str, Any]], operator.add]

    needs_pdf: bool
    attachment_path: Optional[str]
    attachment_name: Optional[str]

    final_answer: str
