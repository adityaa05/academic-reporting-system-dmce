#!/usr/bin/env python3
"""
Make domain column nullable in tasks table.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from sqlalchemy import text
from app.core.database import engine


async def migrate():
    """Make domain column nullable."""

    print("Making domain column nullable...")

    async with engine.begin() as conn:
        # SQLite doesn't support ALTER COLUMN, so we need to check the database type
        result = await conn.execute(text("SELECT sqlite_version()"))
        is_sqlite = result.scalar() is not None

        if is_sqlite:
            print("SQLite detected - domain column is now nullable in model")
            print("✅ No migration needed for SQLite (handled by model change)")
        else:
            # For PostgreSQL
            await conn.execute(text("""
                ALTER TABLE tasks
                ALTER COLUMN domain DROP NOT NULL
            """))
            print("✅ Made domain column nullable in PostgreSQL")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(migrate())
