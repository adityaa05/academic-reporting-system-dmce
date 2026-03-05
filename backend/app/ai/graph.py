# backend/app/ai/graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.ai.state import ReportingState

# Import node execution logic
from app.ai.nodes.intake import intake_node
from app.ai.nodes.summarizer import summarization_node


def dispatch_node(state: ReportingState) -> dict:
    """
    Executes the database insertion of the finalized, approved report.
    Implementation pending database setup.
    """
    return {"db_insertion_status": "SUCCESS"}


def route_post_summarization(state: ReportingState) -> str:
    """
    Evaluates human-in-the-loop validation status to determine execution path.
    """
    if state.get("is_approved"):
        return "dispatch"
    return END


def build_reporting_graph():
    """
    Compiles the state graph architecture and applies the checkpointing mechanism.
    """
    workflow = StateGraph(ReportingState)

    workflow.add_node("intake", intake_node)
    workflow.add_node("summarize", summarization_node)
    workflow.add_node("dispatch", dispatch_node)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "summarize")

    workflow.add_conditional_edges(
        "summarize", route_post_summarization, {"dispatch": "dispatch", END: END}
    )

    workflow.add_edge("dispatch", END)

    memory = MemorySaver()

    app = workflow.compile(checkpointer=memory, interrupt_after=["summarize"])

    return app


reporting_agent = build_reporting_graph()
