#!/usr/bin/env python3
"""
Fix corrupted domain values in the database.

The bug was storing task titles (like "Task 01: Completed Theory Lectures")
in the domain field which is an ENUM that only accepts:
PEDAGOGY, ADMINISTRATION, RESEARCH, EVALUATION, OTHER
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from sqlalchemy import update, text
from app.core.database import engine, AsyncSessionLocal
from app.models.domain import Task as TaskModel
from app.schemas.payload import OperationalDomain


async def fix_corrupted_domains():
    """Fix all corrupted domain values in the database."""

    print("=" * 60)
    print("FIXING CORRUPTED DOMAIN VALUES")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            # First, check how many corrupted records exist
            result = await session.execute(
                text("""
                    SELECT COUNT(*) as count
                    FROM tasks
                    WHERE domain NOT IN ('PEDAGOGY', 'ADMINISTRATION', 'RESEARCH', 'EVALUATION', 'OTHER')
                """)
            )
            count = result.scalar()

            print(f"\nFound {count} corrupted records")

            if count == 0:
                print("✅ No corrupted records found. Database is clean!")
                return

            # Show some examples
            print("\nExamples of corrupted data:")
            result = await session.execute(
                text("""
                    SELECT id, domain, action, metric
                    FROM tasks
                    WHERE domain NOT IN ('PEDAGOGY', 'ADMINISTRATION', 'RESEARCH', 'EVALUATION', 'OTHER')
                    LIMIT 5
                """)
            )
            for row in result:
                print(f"  ID {row.id}: domain='{row.domain[:50]}...'")

            # Fix all corrupted records
            print(f"\nFixing {count} records...")
            await session.execute(
                text("""
                    UPDATE tasks
                    SET domain = 'OTHER'
                    WHERE domain NOT IN ('PEDAGOGY', 'ADMINISTRATION', 'RESEARCH', 'EVALUATION', 'OTHER')
                """)
            )

            await session.commit()

            print(f"✅ Fixed {count} corrupted records")
            print("   All invalid domains have been set to 'OTHER'")

        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(fix_corrupted_domains())
