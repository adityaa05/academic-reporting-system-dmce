# backend/app/api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import uuid

from app.core.database import get_db
from app.schemas.payload import RawTaskInput, ReportApproval, DailySummaryReport
from app.ai.graph import reporting_agent
from app.models.domain import Professor

router = APIRouter()


def get_thread_config(professor_id: str) -> dict:
    """
    Generates a deterministic thread configuration for LangGraph state persistence.
    Binds the session to the specific professor and the current calendar day.
    """
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    thread_id = f"thread_{professor_id}_{current_date}"
    return {"configurable": {"thread_id": thread_id}}


@router.post("/tasks/intake", status_code=status.HTTP_200_OK)
async def log_task(payload: RawTaskInput):
    """
    Ingests raw task text, executes the Task Intake Agent for classification,
    and appends the standardized task to the daily LangGraph state.
    """
    config = get_thread_config(payload.professor_id)

    # Update the graph state with the new raw input
    # The intake_node will process this latest input
    state_update = {
        "professor_id": payload.professor_id,
        "raw_inputs": [payload.raw_input],
    }

    try:
        # Execute the graph up to the current active node
        result = reporting_agent.invoke(state_update, config=config)
        return {
            "status": "success",
            "categorized_tasks": result.get("categorized_tasks", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate", response_model=DailySummaryReport)
async def generate_draft_report(professor_id: str):
    """
    Triggers the Summarization Agent to compile accumulated tasks into a draft report.
    The graph will execute and subsequently pause at the HITL checkpoint.
    """
    config = get_thread_config(professor_id)

    try:
        # LangGraph automatically respects the interrupt_after=["summarize"] defined in graph.py
        result = reporting_agent.invoke({"professor_id": professor_id}, config=config)

        draft = result.get("draft_report")
        if not draft:
            raise HTTPException(
                status_code=404, detail="No tasks available for summarization."
            )

        return draft
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/dispatch")
async def dispatch_final_report(
    payload: ReportApproval, db: AsyncSession = Depends(get_db)
):
    """
    Resumes the LangGraph execution post-validation.
    Routes the approved data to the Dispatch Agent for persistent database storage.
    """
    config = get_thread_config(payload.professor_id)

    if not payload.is_approved:
        raise HTTPException(
            status_code=400, detail="Report must be approved for dispatch."
        )

    # Inject the approval status into the frozen state to satisfy the conditional edge
    state_update = {"is_approved": True}

    if payload.edited_summary:
        # If the human modified the text, update the draft in the state before dispatch
        # Implementation depends on how deeply we want to mutate the Pydantic object in state
        pass

    try:
        # Resuming the graph will trigger the dispatch_node
        result = reporting_agent.invoke(state_update, config=config)
        return {"status": "dispatched", "db_status": result.get("db_insertion_status")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
