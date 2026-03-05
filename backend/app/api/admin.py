# backend/app/api/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel, EmailStr
from typing import List

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.domain import Professor, DailyReport, Task
from app.api.dependencies import get_current_hod

router = APIRouter()


class ProfessorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    department: str = "IT"
    role: str = "FACULTY"


class ProfessorUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    department: str | None = None
    role: str | None = None
    password: str | None = None


class ProfessorResponse(BaseModel):
    id: str
    name: str
    email: str
    department: str
    role: str
    reports_to_id: str | None

    class Config:
        from_attributes = True


@router.get("/users", response_model=List[ProfessorResponse])
async def list_users(
    current_user: Professor = Depends(get_current_hod),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users in the department.
    Only accessible by HOD.
    """
    result = await db.execute(
        select(Professor)
        .where(Professor.department == current_user.department)
        .order_by(Professor.role.desc(), Professor.name)
    )
    users = result.scalars().all()
    return users


@router.post("/users", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: ProfessorCreate,
    current_user: Professor = Depends(get_current_hod),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new faculty member or HOD.
    Only accessible by HOD.
    """
    # Check if email already exists
    result = await db.execute(
        select(Professor).where(Professor.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Generate unique professor ID
    import hashlib
    import time

    id_string = f"{user_data.email}{time.time()}"
    hash_suffix = hashlib.md5(id_string.encode()).hexdigest()[:8]
    role_prefix = "hod" if user_data.role == "HOD" else "prof"
    professor_id = f"{role_prefix}_{user_data.department.lower()}_{hash_suffix}"

    # Create new professor
    password_hash = get_password_hash(user_data.password)
    new_professor = Professor(
        id=professor_id,
        name=user_data.name,
        email=user_data.email,
        password_hash=password_hash,
        department=user_data.department,
        role=user_data.role,
        reports_to_id=current_user.id if user_data.role == "FACULTY" else None,
    )

    db.add(new_professor)
    await db.commit()
    await db.refresh(new_professor)

    return new_professor


@router.put("/users/{professor_id}", response_model=ProfessorResponse)
async def update_user(
    professor_id: str,
    user_data: ProfessorUpdate,
    current_user: Professor = Depends(get_current_hod),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a user's information.
    Only accessible by HOD.
    """
    # Get the professor
    result = await db.execute(
        select(Professor).where(Professor.id == professor_id)
    )
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check department access
    if professor.department != current_user.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only manage users in your department",
        )

    # Update fields
    if user_data.name is not None:
        professor.name = user_data.name
    if user_data.email is not None:
        # Check if email is already taken
        email_check = await db.execute(
            select(Professor).where(
                Professor.email == user_data.email,
                Professor.id != professor_id
            )
        )
        if email_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        professor.email = user_data.email
    if user_data.department is not None:
        professor.department = user_data.department
    if user_data.role is not None:
        professor.role = user_data.role
    if user_data.password is not None:
        professor.password_hash = get_password_hash(user_data.password)

    await db.commit()
    await db.refresh(professor)

    return professor


@router.delete("/users/{professor_id}")
async def delete_user(
    professor_id: str,
    current_user: Professor = Depends(get_current_hod),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a user and all their reports.
    Only accessible by HOD.
    """
    # Get the professor
    result = await db.execute(
        select(Professor).where(Professor.id == professor_id)
    )
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check department access
    if professor.department != current_user.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only manage users in your department",
        )

    # Prevent self-deletion
    if professor.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # First, get all report IDs for this professor
    result = await db.execute(
        select(DailyReport.id).where(DailyReport.professor_id == professor_id)
    )
    report_ids = [row[0] for row in result.all()]

    # Delete tasks associated with those reports
    if report_ids:
        await db.execute(
            delete(Task).where(Task.report_id.in_(report_ids))
        )

    # Delete all reports
    await db.execute(
        delete(DailyReport).where(DailyReport.professor_id == professor_id)
    )

    # Delete the professor
    await db.delete(professor)
    await db.commit()

    return {"status": "success", "message": f"User {professor.name} deleted successfully"}


@router.post("/users/{professor_id}/reset-password")
async def reset_password(
    professor_id: str,
    new_password: str,
    current_user: Professor = Depends(get_current_hod),
    db: AsyncSession = Depends(get_db),
):
    """
    Reset a user's password.
    Only accessible by HOD.
    """
    # Get the professor
    result = await db.execute(
        select(Professor).where(Professor.id == professor_id)
    )
    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check department access
    if professor.department != current_user.department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only manage users in your department",
        )

    # Update password
    professor.password_hash = get_password_hash(new_password)
    await db.commit()

    return {"status": "success", "message": "Password reset successfully"}
