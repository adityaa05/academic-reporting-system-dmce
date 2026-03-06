# backend/app/ai/nodes/intake.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.payload import TaskList
from app.ai.state import ReportingState
from app.core.config import settings
from app.core.institutional_context import get_institutional_context


def intake_node(state: ReportingState) -> dict:
    """
    Executes the LLM sequence to parse raw user input into standardized operational domains.
    Extracts only completed tasks and discards pending or future assignments.
    """
    # Initialize the LLM with the desired model and temperature configuration
    llm = ChatGoogleGenerativeAI(
        model=settings.DEFAULT_MODEL,
        temperature=0.1,
        google_api_key=settings.GOOGLE_API_KEY,
    )

    # Enforce strict adherence to the TaskList schema
    structured_llm = llm.with_structured_output(TaskList)

    # Get institutional context
    context = get_institutional_context()
    context_prompt = context.get_context_prompt()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
        You are an academic data parsing agent. Your objective is to extract completed professional tasks
        from the user's input and categorize them into the defined operational domains.

        {context_prompt}

        Directives:
        1. Only extract tasks that have been completed.
        2. Strictly ignore any tasks marked as "pending", "to-do", or scheduled for the future.
        3. If a duration or numerical metric is provided, extract it into the metric field.
        4. PRESERVE abbreviations and terminology EXACTLY as written in the input.
        5. DO NOT expand or modify abbreviations unless absolutely necessary for clarity.
        6. Treat domain-specific terms (like committee names, internal acronyms) as proper nouns.
        """,
            ),
            ("user", "Raw input: {{raw_input}}"),
        ]
    )

    chain = prompt | structured_llm

    # Process the most recent raw input string from the state
    latest_input = state["raw_inputs"][-1] if state["raw_inputs"] else ""

    if not latest_input:
        return {"categorized_tasks": []}

    result = chain.invoke({"raw_input": latest_input})

    # Return the appended tasks to the state
    return {"categorized_tasks": result.tasks}
