# backend/app/ai/map_reduce.py

import operator
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
import os


class MapReduceState(TypedDict):
    """
    State definition for the Map-Reduce aggregation graph.
    The 'summaries' field uses the operator.add reducer to accumulate parallel outputs.
    """

    raw_reports: List[str]
    summaries: Annotated[list, operator.add]
    final_synthesis: str


async def map_node(state: MapReduceState) -> dict:
    """
    Processes a single report and extracts key institutional metrics.
    Designed to run concurrently across multiple reports.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.1,
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Extract the core academic and administrative achievements from the provided report.",
            ),
            ("user", "{report}"),
        ]
    )

    # In a true parallel map execution, the state passed here contains a single report
    # mapped by the Send API, but for simplicity in this architecture, we process it directly.
    report_content = state["raw_reports"][0]

    chain = prompt | llm
    result = await chain.ainvoke({"report": report_content})

    return {"summaries": [result.content]}


async def reduce_node(state: MapReduceState) -> dict:
    """
    Synthesizes the accumulated summaries into a cohesive departmental overview.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.2,
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
        You are an administrative AI assistant compiling a departmental report for the Head of Department.
        Synthesize the following individual faculty summaries into a comprehensive, unified report.
        Highlight operational bottlenecks, total research output, and pedagogical milestones.
        """,
            ),
            ("user", "Faculty Summaries:\n{summaries}"),
        ]
    )

    combined_summaries = "\n\n---\n\n".join(state["summaries"])

    chain = prompt | llm

    # We will use streaming in the API route, so this node prepares the final string
    # if invoked synchronously, but can be bypassed for SSE streaming.
    result = await chain.ainvoke({"summaries": combined_summaries})

    return {"final_synthesis": result.content}


def build_map_reduce_graph():
    """
    Compiles the Map-Reduce state machine.
    """
    workflow = StateGraph(MapReduceState)

    workflow.add_node("map", map_node)
    workflow.add_node("reduce", reduce_node)

    workflow.set_entry_point("map")
    workflow.add_edge("map", "reduce")
    workflow.add_edge("reduce", END)

    return workflow.compile()


aggregation_agent = build_map_reduce_graph()
