# backend/app/schemas/payload.py

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class OperationalDomain(str, Enum):
    PEDAGOGY = "PEDAGOGY"
    ADMINISTRATION = "ADMINISTRATION"
    RESEARCH = "RESEARCH"
    EVALUATION = "EVALUATION"
    OTHER = "OTHER"


class CategorizedTask(BaseModel):
    domain: OperationalDomain = Field(
        ..., description="The classified operational domain."
    )
    action: str = Field(
        ..., description="A concise description of the completed action."
    )
    metric: Optional[str] = Field(
        None, description="Quantifiable metric, such as duration or count."
    )


class TaskList(BaseModel):
    """
    Wrapper schema to facilitate structured extraction of multiple tasks.
    """

    tasks: List[CategorizedTask] = Field(
        ..., description="List of all extracted and categorized tasks."
    )


class DailySummaryReport(BaseModel):
    executive_summary: str = Field(
        ..., description="A brief paragraph summarizing the day's primary focus."
    )
    completed_activities: List[CategorizedTask] = Field(
        ..., description="List of all categorized tasks."
    )


class RawTaskInput(BaseModel):
    """
    Schema for receiving raw task text from the frontend.
    """

    professor_id: str = Field(..., description="Unique identifier for the professor.")
    raw_input: str = Field(
        ..., description="The unstructured text describing the completed task."
    )


class ReportApproval(BaseModel):
    """
    Schema for receiving the HITL approval signal from the frontend.
    """

    professor_id: str = Field(..., description="Unique identifier for the professor.")
    is_approved: bool = Field(
        ..., description="Boolean indicating if the draft report is validated."
    )
    edited_summary: Optional[str] = Field(
        None, description="Optional edited summary if the user modified the AI draft."
    )
