# backend/app/ai/state.py

from typing import Annotated, List, Optional, TypedDict
import operator
from app.schemas.payload import CategorizedTask, DailySummaryReport


class ReportingState(TypedDict):
    """
    Type definition for the LangGraph state machine governing the daily reporting pipeline.

    Note: Lists use operator.add reducer to accumulate values across node executions
    instead of replacing them.
    """

    professor_id: str
    raw_inputs: Annotated[List[str], operator.add]
    categorized_tasks: Annotated[List[CategorizedTask], operator.add]
    draft_report: Optional[DailySummaryReport]
    is_approved: bool
    db_insertion_status: Optional[str]
