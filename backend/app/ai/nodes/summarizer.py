# backend/app/ai/nodes/summarizer.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.payload import DailySummaryReport
from app.ai.state import ReportingState
import os


def summarization_node(state: ReportingState) -> dict:
    """
    Aggregates the accumulated categorized tasks and synthesizes a formal daily report
    for administrative review.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
    )

    structured_llm = llm.with_structured_output(DailySummaryReport)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
        You are an academic reporting agent. Review the provided list of completed tasks 
        and generate a formal Daily Summary Report.
        
        Directives:
        1. Write a concise, professional executive summary (3-4 sentences maximum) detailing the core focus of the day.
        2. Return the identical list of completed activities provided to you, ensuring all data points remain unaltered.
        """,
            ),
            ("user", "Categorized Tasks: {tasks}"),
        ]
    )

    chain = prompt | structured_llm

    tasks = state.get("categorized_tasks", [])

    if not tasks:
        # Failsafe for empty task lists
        empty_report = DailySummaryReport(
            executive_summary="No completed tasks were logged for this period.",
            completed_activities=[],
        )
        return {"draft_report": empty_report}

    # Format tasks for the prompt context
    task_strings = [
        f"Domain: {t.domain.value}, Action: {t.action}, Metric: {t.metric}"
        for t in tasks
    ]
    tasks_context = "\n".join(task_strings)

    result = chain.invoke({"tasks": tasks_context})

    return {"draft_report": result}
