# backend/app/api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.core.database import get_db
from app.schemas.payload import RawTaskInput, ReportApproval, DailySummaryReport
from app.ai.graph import reporting_agent

router = APIRouter()


def get_thread_config(professor_id: str) -> dict:
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    thread_id = f"thread_{professor_id}_{current_date}"
    return {"configurable": {"thread_id": thread_id}}


@router.post("/tasks/intake", status_code=status.HTTP_200_OK)
async def log_task(payload: RawTaskInput):
    config = get_thread_config(payload.professor_id)
    state_update = {
        "professor_id": payload.professor_id,
        "raw_inputs": [payload.raw_input],
    }
    try:
        # CHANGED: invoke() -> await ainvoke()
        result = await reporting_agent.ainvoke(state_update, config=config)
        return {
            "status": "success",
            "categorized_tasks": result.get("categorized_tasks", []),
        }
    except Exception as e:
        print(f"\n--- AI INTAKE ERROR: {str(e)} ---\n")  # Added logging
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate", response_model=DailySummaryReport)
async def generate_draft_report(professor_id: str):
    config = get_thread_config(professor_id)
    try:
        # CHANGED: invoke() -> await ainvoke()
        result = await reporting_agent.ainvoke(
            {"professor_id": professor_id}, config=config
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
    payload: ReportApproval, db: AsyncSession = Depends(get_db)
):
    config = get_thread_config(payload.professor_id)

    if not payload.is_approved:
        raise HTTPException(
            status_code=400, detail="Report must be approved for dispatch."
        )

    state_update = {"is_approved": True}

    try:
        # CHANGED: invoke() -> await ainvoke()
        result = await reporting_agent.ainvoke(state_update, config=config)
        return {"status": "dispatched", "db_status": result.get("db_insertion_status")}
    except Exception as e:
        print(f"\n--- DISPATCH ERROR: {str(e)} ---\n")
        raise HTTPException(status_code=500, detail=str(e))
