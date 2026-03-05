# backend/app/api/analytics.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.domain import DailyReport, Task
from app.schemas.payload import OperationalDomain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

router = APIRouter()


@router.get("/dashboard/metrics")
async def get_department_metrics(db: AsyncSession = Depends(get_db)):
    """
    Calculates macro-level departmental statistics for the current operational day.
    """
    today = datetime.now(timezone.utc).date()

    try:
        # Calculate total submissions for the day
        report_count_query = select(func.count(DailyReport.id)).where(
            func.date(DailyReport.date_submitted) == today
        )
        report_result = await db.execute(report_count_query)
        total_reports = report_result.scalar() or 0

        # Calculate task distribution across operational domains
        domain_distribution_query = (
            select(Task.domain, func.count(Task.id))
            .join(DailyReport)
            .where(func.date(DailyReport.date_submitted) == today)
            .group_by(Task.domain)
        )
        domain_result = await db.execute(domain_distribution_query)
        distribution = {row[0].value: row[1] for row in domain_result.all()}

        return {
            "date": today.isoformat(),
            "total_submissions": total_reports,
            "domain_distribution": distribution,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/aggregate/stream")
async def stream_department_aggregation(db: AsyncSession = Depends(get_db)):
    """
    Executes a simplified Map-Reduce synthesis of recent reports and streams
    the result to the client via Server-Sent Events (SSE).
    """
    # Fetch all reports from the last 7 days for the synthesis
    query = (
        select(DailyReport.executive_summary)
        .order_by(DailyReport.date_submitted.desc())
        .limit(50)
    )
    result = await db.execute(query)
    reports = result.scalars().all()

    if not reports:
        raise HTTPException(
            status_code=404, detail="Insufficient data for aggregation."
        )

    combined_reports = "\n".join(reports)

    llm = ChatGoogleGenerativeAI(
        model=settings.DEFAULT_MODEL,
        temperature=0.2,
        google_api_key=settings.GOOGLE_API_KEY,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Synthesize the following faculty summaries into a comprehensive departmental report.",
            ),
            ("user", "Summaries:\n{summaries}"),
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
