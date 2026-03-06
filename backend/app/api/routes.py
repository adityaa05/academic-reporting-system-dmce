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
        temperature=0.25,  # Balanced - creative but controlled
        google_api_key=settings.GOOGLE_API_KEY,
    )

    # Create prompt for formatting tasks
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a professional report formatter. Convert brief task notes into formatted entries.

IMPORTANT - JSON FORMAT:
Return ONLY a JSON array of objects. Each object must have exactly 2 fields: "title" and "description".

CORRECT format:
[
  {{
    "title": "Task 01: Your Title Here",
    "description": "Your description here in first person."
  }}
]

WRONG format (DO NOT use this):
[{{"Task 01": {{"title": "...", "description": "..."}}}}]

FORMATTING RULES:
- Title: Start with "Task 01:", "Task 02:", etc. then add a professional description
- Description: 1-2 sentences in first person explaining what was done
- Keep abbreviations as-is (IA, CSI, BE, GITS, etc.)
- DO NOT invent tasks - only format what you're given

EXAMPLES:

Input: "checked ia 1 papers"
Output:
[
  {{
    "title": "Task 01: Checked IA 1 Papers",
    "description": "I reviewed and evaluated the IA 1 examination papers, checking student responses and preparing grades."
  }}
]

Input: "CSI award dist done"
Output:
[
  {{
    "title": "Task 01: Completed CSI Award Distribution",
    "description": "I organized and completed the CSI award distribution ceremony for students."
  }}
]"""),
        ("user", "Format these {task_count} task(s):\n\n{tasks}\n\nReturn a JSON array with {task_count} object(s). Each object needs 'title' and 'description' fields.")
    ])

    # Format tasks for the prompt (use sanitized valid_tasks)
    tasks_text = "\n".join([f"{i+1}. {task}" for i, task in enumerate(valid_tasks)])
    task_count = len(valid_tasks)

    try:
        # Get AI response
        chain = prompt | llm
        result = chain.invoke({"tasks": tasks_text, "task_count": task_count})

        # Parse the AI response
        import json
        import re

        # Extract JSON from the response
        content = result.content
        print(f"\n--- AI Response ---\n{content}\n--- End Response ---\n")
        # Try to find JSON array in the response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            formatted_data = json.loads(json_match.group())

            # Fix wrong JSON format if AI returned nested structure
            # Wrong: [{"Task 01": {"title": "...", "description": "..."}}]
            # Right: [{"title": "Task 01: ...", "description": "..."}]
            if formatted_data and isinstance(formatted_data[0], dict):
                first_item = formatted_data[0]
                # Check if it's the wrong nested format
                if "title" not in first_item and "description" not in first_item:
                    print("\n⚠️  Fixing wrong JSON format from AI...\n")
                    fixed_data = []
                    for item in formatted_data:
                        # Extract the nested data
                        for task_num, task_data in item.items():
                            if isinstance(task_data, dict) and "title" in task_data:
                                # Add "Task XX: " prefix if not present
                                title = task_data["title"]
                                if not title.startswith("Task"):
                                    title = f"{task_num}: {title}"
                                fixed_data.append({
                                    "title": title,
                                    "description": task_data["description"]
                                })
                    formatted_data = fixed_data

            # CRITICAL VALIDATION: Ensure we got exactly the right number of tasks
            if len(formatted_data) > task_count:
                print(f"\n⚠️  WARNING: AI returned {len(formatted_data)} tasks but only {task_count} were provided!")
                print(f"    Truncating to {task_count} tasks to prevent hallucination.\n")
                # Truncate to the correct number
                formatted_data = formatted_data[:task_count]
            elif len(formatted_data) < task_count:
                print(f"\n⚠️  WARNING: AI returned only {len(formatted_data)} tasks but {task_count} were provided!")
                print(f"    Using fallback formatting for missing tasks.\n")
                # Add missing tasks with fallback formatting
                for i in range(len(formatted_data), task_count):
                    task_text = valid_tasks[i]
                    title = task_text.capitalize() if task_text else "Completed Task"
                    formatted_data.append({
                        "title": f"Task {str(i+1).zfill(2)}: {title[:60]}",
                        "description": f"I completed the following work: {task_text}"
                    })
        else:
            # Fallback: create basic formatting with improved descriptions
            formatted_data = []
            for i, task in enumerate(valid_tasks):
                title = task.capitalize() if task else "Completed Task"
                formatted_data.append({
                    "title": f"Task {str(i+1).zfill(2)}: {title[:60]}",
                    "description": f"I completed the following work: {task}"
                })
            print(f"\n⚠️  WARNING: Could not parse AI response, using fallback formatting\n")

        formatted_tasks = [FormattedTask(**item) for item in formatted_data]

        # Cache the formatted report for this professor
        _formatted_reports_cache[current_user.id] = {
            "tasks": formatted_tasks,
            "raw_tasks": valid_tasks,
        }

        return FormattedReportResponse(formatted_tasks=formatted_tasks)

    except Exception as e:
        print(f"\n--- FORMATTING ERROR: {str(e)} ---\n")
        # Fallback formatting with improved descriptions
        formatted_tasks = []
        for i, task in enumerate(valid_tasks):
            title = task.capitalize() if task else "Completed Task"
            formatted_tasks.append(FormattedTask(
                title=f"Task {str(i+1).zfill(2)}: {title[:60]}",
                description=f"I completed the following work: {task}"
            ))

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
            domain=None,  # Not used anymore
            action=task.title,  # Task title
            metric=task.description,  # Task description
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
