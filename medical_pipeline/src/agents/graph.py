from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from langgraph.checkpoint.memory import MemorySaver

from src.agents.orchestrator import orchestrator_node
from src.agents.agent_1_summarizer import summarizer_node
from src.agents.agent_4_email import email_reminder_node
from src.agents.agent_5_comparative import comparative_node
from src.agents.agent_6_retriever import medical_retriever_node
from src.agents.agent_7_statistical import statistical_filter_node
from src.agents.evaluator import evaluator_node

workflow = StateGraph(AgentState)
memory = MemorySaver()

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("summarizer_agent", summarizer_node)
workflow.add_node("medical_retriever_agent", medical_retriever_node)
workflow.add_node("email_reminder_agent", email_reminder_node)
workflow.add_node("comparative_agent", comparative_node)
workflow.add_node("statistical_filter_agent", statistical_filter_node)
workflow.add_node("evaluator_agent", evaluator_node)

workflow.set_entry_point("orchestrator")


def route_next_node(state: AgentState):
    valid_nodes = {
        "summarizer_agent",
        "medical_retriever_agent",
        "email_reminder_agent",
        "comparative_agent",
        "statistical_filter_agent",
    }

    next_node = state.get("next_node")
    if next_node not in valid_nodes:
        return "medical_retriever_agent"

    return next_node


workflow.add_conditional_edges(
    "orchestrator",
    route_next_node,
    {node: node for node in [
        "summarizer_agent",
        "medical_retriever_agent",
        "email_reminder_agent",
        "comparative_agent",
        "statistical_filter_agent"
    ]},
)

for agent_node in [
    "summarizer_agent",
    "medical_retriever_agent",
    "email_reminder_agent",
    "comparative_agent",
]:
    workflow.add_edge(agent_node, END)

workflow.add_edge("statistical_filter_agent", "evaluator_agent")

workflow.add_edge("evaluator_agent", END)

app = workflow.compile(checkpointer=memory)
