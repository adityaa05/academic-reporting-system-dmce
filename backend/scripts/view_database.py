#!/usr/bin/env python3
"""
Database viewer script - view all data in the database.

Usage:
    uv run python scripts/view_database.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.domain import Professor, DailyReport, Task


async def view_database():
    """View all data in the database."""

    async with AsyncSessionLocal() as db:
        print("\n" + "="*80)
        print("📊 DATABASE CONTENTS")
        print("="*80)

        # View Professors
        print("\n👥 PROFESSORS:")
        print("-" * 80)
        result = await db.execute(select(Professor))
        professors = result.scalars().all()

        if not professors:
            print("   No professors found.")
        else:
            for prof in professors:
                print(f"   ID: {prof.id}")
                print(f"   Name: {prof.name}")
                print(f"   Email: {prof.email}")
                print(f"   Department: {prof.department}")
                print(f"   Role: {prof.role}")
                print(f"   Reports To: {prof.reports_to_id or 'None'}")
                print()

        # View Reports
        print("\n📄 DAILY REPORTS:")
        print("-" * 80)
        result = await db.execute(
            select(DailyReport)
            .order_by(DailyReport.date_submitted.desc())
        )
        reports = result.scalars().all()

        if not reports:
            print("   No reports found.")
        else:
            for report in reports:
                print(f"   Report ID: {report.id}")
                print(f"   Professor ID: {report.professor_id}")

                # Get professor name
                prof_result = await db.execute(
                    select(Professor).where(Professor.id == report.professor_id)
                )
                prof = prof_result.scalar_one_or_none()
                if prof:
                    print(f"   Professor Name: {prof.name}")

                print(f"   Date Submitted: {report.date_submitted}")
                print(f"   Summary: {report.executive_summary[:100]}...")

                # Count tasks
                task_result = await db.execute(
                    select(func.count(Task.id)).where(Task.report_id == report.id)
                )
                task_count = task_result.scalar()
                print(f"   Tasks: {task_count}")
                print()

        # View Tasks
        print("\n✅ TASKS:")
        print("-" * 80)
        result = await db.execute(select(Task))
        tasks = result.scalars().all()

        if not tasks:
            print("   No tasks found.")
        else:
            for task in tasks:
                print(f"   Task ID: {task.id}")
                print(f"   Report ID: {task.report_id}")
                print(f"   Domain: {task.domain.value}")
                print(f"   Action: {task.action}")
                print(f"   Metric: {task.metric or 'None'}")
                print()

        # Statistics
        print("\n📈 STATISTICS:")
        print("-" * 80)
        print(f"   Total Professors: {len(professors)}")
        print(f"   Total Reports: {len(reports)}")
        print(f"   Total Tasks: {len(tasks)}")

        # Reports by department
        if professors:
            for dept in set(p.department for p in professors):
                dept_prof_ids = [p.id for p in professors if p.department == dept]
                dept_report_count = sum(1 for r in reports if r.professor_id in dept_prof_ids)
                print(f"   {dept} Department Reports: {dept_report_count}")

        print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(view_database())
