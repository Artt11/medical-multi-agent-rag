from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from langgraph.checkpoint.memory import MemorySaver
from src.agents.orchestrator import orchestrator_node
from src.agents.agent_1_summarizer import summarizer_node
from src.agents.agent_2_cohort import disease_cohort_node
from src.agents.agent_3_temporal import temporal_disease_node
from src.agents.agent_4_email import email_reminder_node
from src.agents.agent_5_comparative import comparative_node
from src.agents.agent_6_source import source_retriever_node
from src.agents.agent_7_statistical import statistical_filter_node
from src.agents.agent_8_notifier import auto_notifier_node

workflow = StateGraph(AgentState)
memory = MemorySaver()

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("summarizer_agent", summarizer_node)
workflow.add_node("disease_cohort_agent", disease_cohort_node)
workflow.add_node("temporal_disease_agent", temporal_disease_node)
workflow.add_node("email_reminder_agent", email_reminder_node)
workflow.add_node("comparative_agent", comparative_node)
workflow.add_node("source_retriever_agent", source_retriever_node)
workflow.add_node("statistical_filter_agent", statistical_filter_node)
workflow.add_node("auto_notifier_agent", auto_notifier_node)

# Entry point
workflow.set_entry_point("orchestrator")


def route_next_node(state: AgentState):
    """
    Safe router that ensures the orchestrator returns a valid agent.
    If an invalid value appears, fallback to summarizer_agent.
    """
    # steice chexac agentnery voronq chkan jnjel
    valid_nodes = {
        "summarizer_agent",
        "disease_cohort_agent",
        "temporal_disease_agent",
        "email_reminder_agent",
        "comparative_agent",
        "source_retriever_agent",
        "statistical_filter_agent",
        "auto_notifier_agent",
    }

    next_node = state.get("next_node")

    if next_node not in valid_nodes:
        return "summarizer_agent"

    return next_node


# steice chexac agentnery voronq chkan jnjel
workflow.add_conditional_edges(
    "orchestrator",
    route_next_node,
    {
        "summarizer_agent": "summarizer_agent",
        "disease_cohort_agent": "disease_cohort_agent",
        "temporal_disease_agent": "temporal_disease_agent",
        "email_reminder_agent": "email_reminder_agent",
        "comparative_agent": "comparative_agent",
        "source_retriever_agent": "source_retriever_agent",
        "statistical_filter_agent": "statistical_filter_agent",
        "auto_notifier_agent": "auto_notifier_agent",
    },
)

# All agents terminate the workflow
for agent in [
    "summarizer_agent",
    "disease_cohort_agent",
    "temporal_disease_agent",
    "email_reminder_agent",
    "comparative_agent",
    "source_retriever_agent",
    "statistical_filter_agent",
    "auto_notifier_agent",
]:
    workflow.add_edge(agent, END)

# app = workflow.compile()
app = workflow.compile(checkpointer=memory)
