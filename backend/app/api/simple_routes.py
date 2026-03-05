# backend/app/api/simple_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, date, timezone
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_hod
from app.models.domain import Professor, DailyReport, Task as TaskModel

router = APIRouter()


class SimpleTask(BaseModel):
    title: str
    description: str


class SimpleTaskList(BaseModel):
    tasks: List[SimpleTask]


class SimpleReport(BaseModel):
    id: int
    professor_id: str
    professor_name: str
    date_submitted: datetime
    tasks: List[dict]

    class Config:
        from_attributes = True


@router.post("/simple/tasks", status_code=status.HTTP_201_CREATED)
async def add_simple_task(
    task: SimpleTask,
    current_user: Professor = Depends(get_current_user),
):
    """
    Add a simple task (title + description).
    This is stored in frontend state, not backend yet.
    """
    return {
        "status": "success",
        "task": {
            "title": task.title,
            "description": task.description,
        },
    }


@router.post("/simple/reports/submit")
async def submit_simple_report(
    payload: SimpleTaskList,
    current_user: Professor = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a daily report with simple tasks.
    No AI categorization - just title + description.
    """
    if not payload.tasks or len(payload.tasks) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one task is required to submit a report.",
        )

    # Check if report already exists for today
    today = datetime.now(timezone.utc).date()
    existing_report = await db.execute(
        select(DailyReport).where(
            DailyReport.professor_id == current_user.id,
            func.date(DailyReport.date_submitted) == today,
        )
    )
    existing = existing_report.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You have already submitted a report for today.",
        )

    # Create summary from tasks
    summary = f"{current_user.name} completed {len(payload.tasks)} tasks today."

    # Create daily report
    new_report = DailyReport(
        professor_id=current_user.id,
        executive_summary=summary,
    )
    db.add(new_report)
    await db.flush()

    # Add tasks to the report
    for idx, task in enumerate(payload.tasks, 1):
        new_task = TaskModel(
            report_id=new_report.id,
            domain=f"Task {idx:02d}",  # Store task number as domain
            action=task.title,
            metric=task.description,
        )
        db.add(new_task)

    await db.commit()
    await db.refresh(new_report)

    return {
        "status": "success",
        "message": "Report submitted successfully!",
        "report_id": new_report.id,
    }


@router.get("/simple/reports/my-history", response_model=List[SimpleReport])
async def get_my_report_history(
    current_user: Professor = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 30,
):
    """
    Get report history for the current user.
    """
    result = await db.execute(
        select(DailyReport)
        .where(DailyReport.professor_id == current_user.id)
        .order_by(desc(DailyReport.date_submitted))
        .limit(limit)
    )
    reports = result.scalars().all()

    response = []
    for report in reports:
        # Get tasks for this report
        tasks_result = await db.execute(
            select(TaskModel).where(TaskModel.report_id == report.id)
        )
        tasks = tasks_result.scalars().all()

        response.append(
            {
                "id": report.id,
                "professor_id": report.professor_id,
                "professor_name": current_user.name,
                "date_submitted": report.date_submitted,
                "tasks": [
                    {
                        "title": t.action if t.action else t.domain,  # Title from action or domain
                        "description": t.metric if t.metric else "",  # Description from metric
                    }
                    for t in tasks
                ],
            }
        )

    return response


@router.get("/simple/reports/all", response_model=List[SimpleReport])
async def get_all_faculty_reports(
    current_user: Professor = Depends(get_current_hod),
    db: AsyncSession = Depends(get_db),
    days: int = 30,
):
    """
    Get all faculty reports in HOD's department.
    Only accessible by HOD.
    """
    # Get all reports from the HOD's department
    result = await db.execute(
        select(DailyReport, Professor)
        .join(Professor, DailyReport.professor_id == Professor.id)
        .where(Professor.department == current_user.department)
        .order_by(desc(DailyReport.date_submitted), Professor.name)
        .limit(days * 10)  # Approximate limit
    )
    rows = result.all()

    response = []
    for report, professor in rows:
        # Get tasks for this report
        tasks_result = await db.execute(
            select(TaskModel).where(TaskModel.report_id == report.id)
        )
        tasks = tasks_result.scalars().all()

        response.append(
            {
                "id": report.id,
                "professor_id": report.professor_id,
                "professor_name": professor.name,
                "date_submitted": report.date_submitted,
                "tasks": [
                    {
                        "title": t.action if t.action else t.domain,  # Title from action or domain
                        "description": t.metric if t.metric else "",  # Description from metric
                    }
                    for t in tasks
                ],
            }
        )

    return response


@router.get("/simple/reports/new-count")
async def get_new_reports_count(
    current_user: Professor = Depends(get_current_hod),
    db: AsyncSession = Depends(get_db),
):
    """
    Get count of reports submitted today (for notifications).
    Only accessible by HOD.
    """
    today = datetime.now(timezone.utc).date()

    result = await db.execute(
        select(func.count(DailyReport.id))
        .join(Professor, DailyReport.professor_id == Professor.id)
        .where(
            Professor.department == current_user.department,
            func.date(DailyReport.date_submitted) == today,
        )
    )
    count = result.scalar()

    return {
        "date": today,
        "new_reports": count,
    }
