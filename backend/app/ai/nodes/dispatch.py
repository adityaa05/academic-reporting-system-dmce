# backend/app/ai/nodes/dispatch.py

from app.ai.state import ReportingState
from app.core.database import AsyncSessionLocal
from app.models.domain import DailyReport, Task


async def dispatch_node(state: ReportingState) -> dict:
    """
    Executes the asynchronous database transaction to persist the finalized
    daily report and its associated tasks into PostgreSQL.
    """
    draft_report = state.get("draft_report")
    professor_id = state.get("professor_id")

    if not draft_report or not professor_id:
        return {"db_insertion_status": "FAILED_MISSING_DATA"}

    async with AsyncSessionLocal() as session:
        try:
            # Initialize the report entity
            new_report = DailyReport(
                professor_id=professor_id,
                executive_summary=draft_report.executive_summary,
            )
            session.add(new_report)

            # Flush the session to assign an ID to new_report without committing the transaction
            await session.flush()

            # Initialize and map the associated tasks using the new report ID
            tasks_to_insert = []
            for task_data in draft_report.completed_activities:
                new_task = Task(
                    report_id=new_report.id,
                    domain=task_data.domain,
                    action=task_data.action,
                    metric=task_data.metric,
                )
                tasks_to_insert.append(new_task)

            session.add_all(tasks_to_insert)

            # Commit the full transaction to the database
            await session.commit()

            return {"db_insertion_status": "SUCCESS"}

        except Exception as e:
            # Rollback the transaction to maintain database integrity in case of failure
            await session.rollback()
            return {"db_insertion_status": f"FAILED_TRANSACTION: {str(e)}"}
