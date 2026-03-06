# backend/app/ai/nodes/summarizer.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.payload import DailySummaryReport
from app.ai.state import ReportingState
from app.core.config import settings
from app.core.institutional_context import get_institutional_context


def summarization_node(state: ReportingState) -> dict:
    """
    Aggregates the accumulated categorized tasks and synthesizes a formal daily report
    for administrative review.
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.DEFAULT_MODEL,
        temperature=0.2,
        google_api_key=settings.GOOGLE_API_KEY,
    )

    structured_llm = llm.with_structured_output(DailySummaryReport)

    # Get institutional context
    context = get_institutional_context()
    context_prompt = context.get_context_prompt()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
        You are an academic reporting agent. Review the provided list of completed tasks
        and generate a formal Daily Summary Report.

        {context_prompt}

        Directives:
        1. Write a concise, professional executive summary (3-4 sentences maximum) detailing the core focus of the day.
        2. Return the identical list of completed activities provided to you, ensuring all data points remain unaltered.
        3. In your executive summary, PRESERVE terminology and abbreviations EXACTLY as they appear in the tasks.
        4. DO NOT expand abbreviations that are not in the institutional context - keep them as-is.
        5. Use institutional context ONLY for known terms; treat unknown terms as proper nouns.
        """,
            ),
            ("user", "Categorized Tasks: {{tasks}}"),
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
