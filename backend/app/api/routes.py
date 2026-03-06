# backend/app/api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.core.database import get_db
from app.core.config import settings
from app.core.institutional_context import get_institutional_context
from app.core.input_sanitizer import get_sanitizer
from app.schemas.payload import RawTaskInput, ReportApproval, DailySummaryReport
from app.ai.graph import reporting_agent
from app.api.dependencies import get_current_user
from app.models.domain import Professor, DailyReport, Task as TaskModel
from pydantic import BaseModel

router = APIRouter()


class ReportHistoryResponse(BaseModel):
    id: int
    date_submitted: datetime
    executive_summary: str
    tasks: List[dict]

    class Config:
        from_attributes = True


class TaskListInput(BaseModel):
    tasks: List[str]  # List of simple one-line task descriptions


class FormattedTask(BaseModel):
    title: str
    description: str


class FormattedReportResponse(BaseModel):
    formatted_tasks: List[FormattedTask]


def get_thread_config(professor_id: str) -> dict:
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    thread_id = f"thread_{professor_id}_{current_date}"
    return {"configurable": {"thread_id": thread_id}}


@router.post("/tasks/intake", status_code=status.HTTP_200_OK)
async def log_task(
    payload: RawTaskInput,
    current_user: Professor = Depends(get_current_user),
):
    """
    Log a task for the current authenticated user.
    Uses the user's ID from the JWT token instead of accepting it in the payload.
    """
    config = get_thread_config(current_user.id)
    state_update = {
        "professor_id": current_user.id,
        "raw_inputs": [payload.raw_input],
    }
    try:
        result = await reporting_agent.ainvoke(state_update, config=config)
        return {
            "status": "success",
            "categorized_tasks": result.get("categorized_tasks", []),
        }
    except Exception as e:
        print(f"\n--- AI INTAKE ERROR: {str(e)} ---\n")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate", response_model=DailySummaryReport)
async def generate_draft_report(
    current_user: Professor = Depends(get_current_user),
):
    """
    Generate a draft report for the current authenticated user.
    """
    config = get_thread_config(current_user.id)
    try:
        result = await reporting_agent.ainvoke(
            {"professor_id": current_user.id}, config=config
        )

        draft = result.get("draft_report")
        if not draft:
            raise HTTPException(
                status_code=404, detail="No tasks available for summarization."
            )

        return draft
    except Exception as e:
        print(f"\n--- SUMMARIZATION ERROR: {str(e)} ---\n")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/dispatch")
async def dispatch_final_report(
    payload: ReportApproval,
    current_user: Professor = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Dispatch the final approved report for the current authenticated user.
    """
    config = get_thread_config(current_user.id)

    if not payload.is_approved:
        raise HTTPException(
            status_code=400, detail="Report must be approved for dispatch."
        )

    state_update = {"is_approved": True}

    try:
        result = await reporting_agent.ainvoke(state_update, config=config)
        return {"status": "dispatched", "db_status": result.get("db_insertion_status")}
    except Exception as e:
        print(f"\n--- DISPATCH ERROR: {str(e)} ---\n")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/history", response_model=List[ReportHistoryResponse])
async def get_report_history(
    current_user: Professor = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    """
    Get report history for the current authenticated user.
    """
    result = await db.execute(
        select(DailyReport)
        .where(DailyReport.professor_id == current_user.id)
        .order_by(DailyReport.date_submitted.desc())
        .limit(limit)
    )
    reports = result.scalars().all()

    # Fetch tasks for each report
    response = []
    for report in reports:
        tasks_result = await db.execute(
            select(TaskModel).where(TaskModel.report_id == report.id)
        )
        tasks = tasks_result.scalars().all()

        response.append(
            ReportHistoryResponse(
                id=report.id,
                date_submitted=report.date_submitted,
                executive_summary=report.executive_summary,
                tasks=[
                    {
                        "domain": task.domain.value,
                        "action": task.action,
                        "metric": task.metric,
                    }
                    for task in tasks
                ],
            )
        )

    return response


# Store formatted reports temporarily in memory (keyed by professor_id)
_formatted_reports_cache = {}


@router.post("/reports/generate-formatted", response_model=FormattedReportResponse)
async def generate_formatted_report(
    payload: TaskListInput,
    current_user: Professor = Depends(get_current_user),
):
    """
    Takes simple one-line task descriptions and uses Gemini AI to format them
    into proper 'Task 01: Title - Description' format using simple language.
    """
    if not payload.tasks or len(payload.tasks) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one task is required to generate a report.",
        )

    # Sanitize and validate input tasks
    sanitizer = get_sanitizer()
    valid_tasks, rejected_tasks = sanitizer.sanitize_and_validate_tasks(payload.tasks)

    if not valid_tasks:
        raise HTTPException(
            status_code=400,
            detail=f"No valid tasks found. Please provide meaningful task descriptions. Rejected: {rejected_tasks[:3]}",
        )

    if rejected_tasks:
        print(f"\nWarning: {len(rejected_tasks)} tasks were filtered out due to low quality: {rejected_tasks}")

    # Initialize Gemini AI
    llm = ChatGoogleGenerativeAI(
        model=settings.DEFAULT_MODEL,
        temperature=0.3,
        google_api_key=settings.GOOGLE_API_KEY,
    )

    # Get institutional context
    context = get_institutional_context(department=current_user.department)
    context_prompt = context.get_context_prompt()

    # Create prompt for formatting tasks
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
You are a helpful assistant that formats faculty work logs into clear, professional reports.

{context_prompt}

Given a list of simple one-line task descriptions, format each one into:
- A clear, descriptive title (what was done)
- A simple paragraph explanation (expanding on the task in plain English)

Use simple, clear language. No fancy words. Write as if explaining to a colleague.

For each task, respond with JSON in this exact format:
{{{{
  "title": "Task 01: [Clear Title Here]",
  "description": "[1-2 sentences explaining what was done in simple words]"
}}}}

IMPORTANT:
- Number tasks as Task 01, Task 02, Task 03, etc.
- Keep language simple and clear
- Write in first person ("I taught...", "I reviewed...")
- ONLY expand abbreviations that are in the INSTITUTIONAL CONTEXT above
- For unknown abbreviations or terms, keep them EXACTLY as written - DO NOT guess or make up expansions
- Be specific but concise
- When you see abbreviations not in the context, treat them as proper nouns and keep them unchanged
"""),
        ("user", """
Format these tasks into a proper report:

{{tasks}}

Return a JSON array of formatted tasks.
""")
    ])

    # Format tasks for the prompt (use sanitized valid_tasks)
    tasks_text = "\n".join([f"{i+1}. {task}" for i, task in enumerate(valid_tasks)])

    try:
        # Get AI response
        chain = prompt | llm
        result = chain.invoke({"tasks": tasks_text})

        # Parse the AI response
        import json
        import re

        # Extract JSON from the response
        content = result.content
        # Try to find JSON array in the response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            formatted_data = json.loads(json_match.group())
        else:
            # Fallback: create basic formatting
            formatted_data = [
                {
                    "title": f"Task {str(i+1).zfill(2)}: {task[:50]}",
                    "description": f"Completed: {task}"
                }
                for i, task in enumerate(valid_tasks)
            ]

        formatted_tasks = [FormattedTask(**item) for item in formatted_data]

        # Cache the formatted report for this professor
        _formatted_reports_cache[current_user.id] = {
            "tasks": formatted_tasks,
            "raw_tasks": valid_tasks,
        }

        return FormattedReportResponse(formatted_tasks=formatted_tasks)

    except Exception as e:
        print(f"\n--- FORMATTING ERROR: {str(e)} ---\n")
        # Fallback formatting
        formatted_tasks = [
            FormattedTask(
                title=f"Task {str(i+1).zfill(2)}: {task[:50]}",
                description=task
            )
            for i, task in enumerate(valid_tasks)
        ]

        _formatted_reports_cache[current_user.id] = {
            "tasks": formatted_tasks,
            "raw_tasks": valid_tasks,
        }

        return FormattedReportResponse(formatted_tasks=formatted_tasks)


@router.post("/reports/dispatch-formatted")
async def dispatch_formatted_report(
    payload: ReportApproval,
    current_user: Professor = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Saves the AI-formatted report to the database.
    """
    if not payload.is_approved:
        raise HTTPException(
            status_code=400, detail="Report must be approved for submission."
        )

    # Get the cached formatted report
    cached_report = _formatted_reports_cache.get(current_user.id)
    if not cached_report:
        raise HTTPException(
            status_code=404, detail="No formatted report found. Please generate a report first."
        )

    formatted_tasks = cached_report["tasks"]

    # Check if report already exists for today
    today = datetime.now(timezone.utc).date()
    existing_report = await db.execute(
        select(DailyReport).where(
            DailyReport.professor_id == current_user.id,
            func.date(DailyReport.date_submitted) == today,
        )
    )
    if existing_report.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="You have already submitted a report for today.",
        )

    # Create executive summary
    summary = f"{current_user.name} completed {len(formatted_tasks)} tasks today."

    # Create daily report
    new_report = DailyReport(
        professor_id=current_user.id,
        executive_summary=summary,
    )
    db.add(new_report)
    await db.flush()

    # Add formatted tasks to the report
    for task in formatted_tasks:
        new_task = TaskModel(
            report_id=new_report.id,
            domain=task.title,  # Store full title in domain field
            action=task.title,  # Store title in action
            metric=task.description,  # Store description in metric
        )
        db.add(new_task)

    await db.commit()
    await db.refresh(new_report)

    # Clear the cache
    if current_user.id in _formatted_reports_cache:
        del _formatted_reports_cache[current_user.id]

    return {
        "status": "success",
        "message": "Report submitted successfully!",
        "report_id": new_report.id,
    }
