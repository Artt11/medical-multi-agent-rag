from typing import Annotated, List, TypedDict, Optional, Any, Dict
import operator


class AgentState(TypedDict):
    query: str

    next_node: str
    patient_id: Optional[str]
    timeframe: Optional[str]
    disease: Optional[str]

    context_chunks: Annotated[List[str], operator.add]
    sql_results: Annotated[List[Dict[str, Any]], operator.add]

    final_answer: str
