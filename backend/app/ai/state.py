# backend/app/ai/state.py

from typing import TypedDict, List, Optional
from app.schemas.payload import CategorizedTask, DailySummaryReport


class ReportingState(TypedDict):
    """
    Type definition for the LangGraph state machine governing the daily reporting pipeline.
    """

    professor_id: str
    raw_inputs: List[str]
    categorized_tasks: List[CategorizedTask]
    draft_report: Optional[DailySummaryReport]
    is_approved: bool
    db_insertion_status: Optional[str]
