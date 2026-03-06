# backend/app/api/analytics.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import List, Dict

from app.core.database import get_db
from app.models.domain import DailyReport, Task, Professor
from app.schemas.payload import OperationalDomain
from app.api.dependencies import get_current_hod, get_current_user
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

router = APIRouter()


class DomainDistribution(BaseModel):
    domain: str
    count: int
    percentage: float


class RecentSubmission(BaseModel):
    professor: str
    time: str
    tasks: int


class WeeklyTrend(BaseModel):
    day: str
    submissions: int


class DepartmentStats(BaseModel):
    total_faculty: int
    reports_today: int
    completion_rate: int
    top_domains: List[DomainDistribution]
    recent_submissions: List[RecentSubmission]
    weekly_trend: List[WeeklyTrend]


@router.get("/dashboard/metrics")
async def get_department_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: Professor = Depends(get_current_user),
):
    """
    Calculates macro-level departmental statistics for the current operational day.
    """
    today = datetime.now(timezone.utc).date()

    try:
        # Filter by department
        department_filter = Professor.department == current_user.department

        # Calculate total submissions for the day
        report_count_query = (
            select(func.count(DailyReport.id))
            .join(Professor)
            .where(func.date(DailyReport.date_submitted) == today)
            .where(department_filter)
        )
        report_result = await db.execute(report_count_query)
        total_reports = report_result.scalar() or 0

        return {
            "date": today.isoformat(),
            "total_submissions": total_reports,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hod/stats", response_model=DepartmentStats)
async def get_hod_department_stats(
    current_user: Professor = Depends(get_current_hod),
    db: AsyncSession = Depends(get_db),
):
    """
    Comprehensive department statistics for HOD dashboard.
    Only accessible by HOD role.
    """
    today = datetime.now(timezone.utc).date()
    department_filter = Professor.department == current_user.department

    # Total faculty in department
    faculty_count_query = select(func.count(Professor.id)).where(department_filter)
    faculty_result = await db.execute(faculty_count_query)
    total_faculty = faculty_result.scalar() or 0

    # Reports submitted today
    reports_today_query = (
        select(func.count(DailyReport.id))
        .join(Professor)
        .where(func.date(DailyReport.date_submitted) == today)
        .where(department_filter)
    )
    reports_today_result = await db.execute(reports_today_query)
    reports_today = reports_today_result.scalar() or 0

    # Completion rate
    completion_rate = (
        int((reports_today / total_faculty) * 100) if total_faculty > 0 else 0
    )

    # Domain categorization removed - not used anymore
    top_domains = []

    # Recent submissions (last 10)
    recent_query = (
        select(Professor.name, DailyReport.date_submitted, func.count(Task.id))
        .join(DailyReport, DailyReport.professor_id == Professor.id)
        .join(Task, Task.report_id == DailyReport.id)
        .where(department_filter)
        .group_by(Professor.name, DailyReport.date_submitted, DailyReport.id)
        .order_by(DailyReport.date_submitted.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_query)
    recent_rows = recent_result.all()

    recent_submissions = []
    for row in recent_rows:
        time_diff = datetime.now(timezone.utc) - row[1].replace(tzinfo=timezone.utc)
        if time_diff.days > 0:
            time_str = f"{time_diff.days} days ago"
        elif time_diff.seconds // 3600 > 0:
            time_str = f"{time_diff.seconds // 3600} hours ago"
        else:
            time_str = f"{time_diff.seconds // 60} mins ago"

        recent_submissions.append(
            RecentSubmission(professor=row[0], time=time_str, tasks=row[2])
        )

    # Weekly trend (last 7 days)
    weekly_trend = []
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for i in range(7):
        day = today - timedelta(days=6 - i)
        count_query = (
            select(func.count(DailyReport.id))
            .join(Professor)
            .where(func.date(DailyReport.date_submitted) == day)
            .where(department_filter)
        )
        count_result = await db.execute(count_query)
        count = count_result.scalar() or 0

        day_name = day_names[day.weekday()]
        weekly_trend.append(WeeklyTrend(day=day_name, submissions=count))

    return DepartmentStats(
        total_faculty=total_faculty,
        reports_today=reports_today,
        completion_rate=completion_rate,
        top_domains=top_domains,
        recent_submissions=recent_submissions,
        weekly_trend=weekly_trend,
    )


@router.get("/reports/aggregate/stream")
async def stream_department_aggregation(
    current_user: Professor = Depends(get_current_hod),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes a simplified Map-Reduce synthesis of recent reports and streams
    the result to the client via Server-Sent Events (SSE).
    Only accessible by HOD role.
    """
    # Fetch reports from the same department, last 50 reports
    query = (
        select(DailyReport.executive_summary)
        .join(Professor)
        .where(Professor.department == current_user.department)
        .order_by(DailyReport.date_submitted.desc())
        .limit(50)
    )
    result = await db.execute(query)
    reports = result.scalars().all()

    if not reports or len(reports) < 10:
        raise HTTPException(
            status_code=404,
            detail=f"Insufficient data for aggregation. Found {len(reports)} reports, need at least 10.",
        )

    combined_reports = "\n\n".join(reports)

    llm = ChatGoogleGenerativeAI(
        model=settings.DEFAULT_MODEL,
        temperature=0.2,
        google_api_key=settings.GOOGLE_API_KEY,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are synthesizing faculty activity reports for the {current_user.department} department. "
                "Create a comprehensive departmental summary that highlights key achievements, trends, and activities. "
                "Structure the report with clear sections and insights.",
            ),
            ("user", "Faculty Report Summaries:\n\n{summaries}"),
        ]
    )

    chain = prompt | llm

    async def event_generator():
        """
        Asynchronous generator yielding formatted SSE data chunks.
        """
        try:
            async for chunk in chain.astream({"summaries": combined_reports}):
                if chunk.content:
                    # Format strictly adheres to the SSE protocol specification
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
