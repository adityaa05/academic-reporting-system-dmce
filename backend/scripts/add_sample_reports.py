#!/usr/bin/env python3
"""
Add sample reports for testing.

Usage:
    uv run python scripts/add_sample_reports.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.domain import Professor, DailyReport, Task
from app.schemas.payload import OperationalDomain
from sqlalchemy import select


async def add_sample_reports():
    """Add sample reports for testing."""

    async with AsyncSessionLocal() as db:
        # Get all faculty members
        result = await db.execute(
            select(Professor).where(Professor.role == "FACULTY")
        )
        faculty = result.scalars().all()

        if not faculty:
            print("❌ No faculty members found. Run seed_database.py first.")
            return

        print(f"📝 Adding sample reports for {len(faculty)} faculty members...\n")

        # Sample reports data
        sample_reports = [
            {
                "summary": "Conducted two lectures on database management systems covering normalization and SQL optimization. Reviewed and graded 20 student assignments. Participated in department meeting regarding curriculum updates for next semester.",
                "tasks": [
                    {"domain": OperationalDomain.PEDAGOGY, "action": "Delivered lecture on DBMS normalization", "metric": "2 hours"},
                    {"domain": OperationalDomain.PEDAGOGY, "action": "Taught SQL optimization techniques", "metric": "1 lecture"},
                    {"domain": OperationalDomain.EVALUATION, "action": "Reviewed and graded student assignments", "metric": "20 submissions"},
                    {"domain": OperationalDomain.ADMINISTRATION, "action": "Attended curriculum meeting", "metric": "1 hour"},
                ]
            },
            {
                "summary": "Focused on research activities including reviewing 5 peer-reviewed papers for conference submission. Prepared teaching materials for upcoming lectures on cloud computing and distributed systems.",
                "tasks": [
                    {"domain": OperationalDomain.RESEARCH, "action": "Reviewed conference papers", "metric": "5 papers"},
                    {"domain": OperationalDomain.PEDAGOGY, "action": "Prepared cloud computing lecture materials", "metric": "3 hours"},
                    {"domain": OperationalDomain.PEDAGOGY, "action": "Created distributed systems examples", "metric": "2 hours"},
                ]
            },
            {
                "summary": "Delivered lectures on machine learning algorithms and conducted practical lab session on neural networks. Mentored 3 final year students on their capstone projects.",
                "tasks": [
                    {"domain": OperationalDomain.PEDAGOGY, "action": "Taught machine learning algorithms", "metric": "2 lectures"},
                    {"domain": OperationalDomain.PEDAGOGY, "action": "Conducted neural networks lab", "metric": "2 hours"},
                    {"domain": OperationalDomain.PEDAGOGY, "action": "Mentored capstone project students", "metric": "3 students"},
                ]
            },
            {
                "summary": "Evaluated student mid-semester exam papers and provided detailed feedback. Organized workshop on career guidance for students. Updated course content based on industry feedback.",
                "tasks": [
                    {"domain": OperationalDomain.EVALUATION, "action": "Evaluated mid-semester exams", "metric": "45 papers"},
                    {"domain": OperationalDomain.ADMINISTRATION, "action": "Organized career guidance workshop", "metric": "2 hours"},
                    {"domain": OperationalDomain.PEDAGOGY, "action": "Updated course curriculum", "metric": "4 hours"},
                ]
            },
            {
                "summary": "Worked on research paper submission for international journal. Conducted online doubt-clearing session for students. Reviewed lab equipment requirements for next semester.",
                "tasks": [
                    {"domain": OperationalDomain.RESEARCH, "action": "Prepared research paper for journal submission", "metric": "5 hours"},
                    {"domain": OperationalDomain.PEDAGOGY, "action": "Conducted doubt-clearing session", "metric": "1 hour"},
                    {"domain": OperationalDomain.ADMINISTRATION, "action": "Reviewed lab equipment needs", "metric": "2 hours"},
                ]
            },
        ]

        # Add reports for each faculty with different dates
        for i, faculty_member in enumerate(faculty):
            # Create report from 1-5 days ago
            days_ago = (i % 5) + 1
            date_submitted = datetime.now() - timedelta(days=days_ago)

            # Use modulo to cycle through sample reports
            report_data = sample_reports[i % len(sample_reports)]

            # Create report
            report = DailyReport(
                professor_id=faculty_member.id,
                date_submitted=date_submitted,
                executive_summary=report_data["summary"],
            )
            db.add(report)
            await db.flush()  # Get the report ID

            # Add tasks for this report
            for task_data in report_data["tasks"]:
                task = Task(
                    report_id=report.id,
                    domain=task_data["domain"],
                    action=task_data["action"],
                    metric=task_data.get("metric"),
                )
                db.add(task)

            print(f"✅ Added report for {faculty_member.name} ({days_ago} days ago)")

        await db.commit()

        print("\n" + "="*60)
        print("🎉 Sample reports added successfully!")
        print("="*60)
        print("\n💡 You can now:")
        print("   1. View database: uv run python scripts/view_database.py")
        print("   2. Login as HOD and see the dashboard populated")
        print("   3. View analytics with real data")


if __name__ == "__main__":
    asyncio.run(add_sample_reports())
