#!/usr/bin/env python3
"""
Database seeding script for Academic Reporting System.

Creates initial users for the IT department including:
- HOD account
- Faculty accounts

Usage:
    python scripts/seed_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import engine, AsyncSessionLocal
from app.models.domain import Professor, Base
from app.core.security import get_password_hash


async def seed_database():
    """Create initial users in the database."""

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if users already exist
        result = await db.execute(select(Professor))
        existing_users = result.scalars().all()

        if existing_users:
            print(f"⚠️  Database already has {len(existing_users)} users.")
            response = input("Do you want to add more users anyway? (y/N): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return

        # Default password for all users (change in production!)
        default_password = "academic123"
        password_hash = get_password_hash(default_password)

        # HOD Account
        hod = Professor(
            id="hod_it_001",
            name="Dr. Rajesh Kumar",
            email="rajesh.kumar@dmce.ac.in",
            password_hash=password_hash,
            department="IT",
            role="HOD",
            reports_to_id=None,
        )

        # Faculty Accounts
        faculty_members = [
            Professor(
                id="prof_it_001",
                name="Dr. Priya Sharma",
                email="priya.sharma@dmce.ac.in",
                password_hash=password_hash,
                department="IT",
                role="FACULTY",
                reports_to_id="hod_it_001",
            ),
            Professor(
                id="prof_it_002",
                name="Dr. Amit Patel",
                email="amit.patel@dmce.ac.in",
                password_hash=password_hash,
                department="IT",
                role="FACULTY",
                reports_to_id="hod_it_001",
            ),
            Professor(
                id="prof_it_003",
                name="Dr. Sneha Desai",
                email="sneha.desai@dmce.ac.in",
                password_hash=password_hash,
                department="IT",
                role="FACULTY",
                reports_to_id="hod_it_001",
            ),
            Professor(
                id="prof_it_004",
                name="Dr. Rahul Mehta",
                email="rahul.mehta@dmce.ac.in",
                password_hash=password_hash,
                department="IT",
                role="FACULTY",
                reports_to_id="hod_it_001",
            ),
            Professor(
                id="prof_it_005",
                name="Dr. Anita Singh",
                email="anita.singh@dmce.ac.in",
                password_hash=password_hash,
                department="IT",
                role="FACULTY",
                reports_to_id="hod_it_001",
            ),
        ]

        # Add all users
        all_users = [hod] + faculty_members

        for user in all_users:
            # Check if email already exists
            result = await db.execute(
                select(Professor).where(Professor.email == user.email)
            )
            if result.scalar_one_or_none():
                print(f"⏭️  Skipping {user.email} - already exists")
                continue

            db.add(user)
            print(f"✅ Added {user.name} ({user.email}) - Role: {user.role}")

        await db.commit()

        print("\n" + "="*60)
        print("🎉 Database seeding completed!")
        print("="*60)
        print(f"\n📝 Default password for all users: {default_password}")
        print("\n👤 Login Credentials:")
        print(f"\nHOD Account:")
        print(f"  Email: {hod.email}")
        print(f"  Password: {default_password}")
        print(f"\nFaculty Accounts:")
        for faculty in faculty_members:
            print(f"  Email: {faculty.email}")
            print(f"  Password: {default_password}")
        print("\n⚠️  IMPORTANT: Change these passwords in production!")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(seed_database())
