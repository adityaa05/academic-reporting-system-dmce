#!/usr/bin/env python3
"""
Database reset script - drops all tables and recreates them.

⚠️  WARNING: This will DELETE ALL DATA in the database!

Usage:
    uv run python scripts/reset_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.models.domain import Professor, DailyReport, Task


async def reset_database():
    """Drop all tables and recreate them with the new schema."""

    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    response = input("Are you sure you want to continue? Type 'YES' to confirm: ")

    if response != 'YES':
        print("Operation cancelled.")
        return

    print("\n🗑️  Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("✅ All tables dropped.")

    print("\n🔨 Creating tables with new schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Tables created successfully!")
    print("\n✨ Database reset complete!")
    print("\n📝 Next step: Run 'uv run python scripts/seed_database.py' to add initial users.")


if __name__ == "__main__":
    asyncio.run(reset_database())
