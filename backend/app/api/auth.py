# backend/app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import timedelta

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.domain import Professor
from app.api.dependencies import get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    department: str = "IT"
    role: str = "FACULTY"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    department: str
    role: str


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT access token.
    """
    # Find user by email
    result = await db.execute(select(Professor).where(Professor.email == request.email))
    professor = result.scalar_one_or_none()

    if not professor or not verify_password(request.password, professor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": professor.id}, expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": professor.id,
            "name": professor.name,
            "email": professor.email,
            "department": professor.department,
            "role": professor.role,
        },
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user (professor/faculty).
    """
    # Check if email already exists
    result = await db.execute(select(Professor).where(Professor.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Generate unique professor ID
    # Format: prof_{department}_{timestamp_hash}
    import hashlib
    import time

    id_string = f"{request.email}{time.time()}"
    hash_suffix = hashlib.md5(id_string.encode()).hexdigest()[:8]
    professor_id = f"prof_{request.department.lower()}_{hash_suffix}"

    # Create new professor
    password_hash = get_password_hash(request.password)
    new_professor = Professor(
        id=professor_id,
        name=request.name,
        email=request.email,
        password_hash=password_hash,
        department=request.department,
        role=request.role,
    )

    db.add(new_professor)
    await db.commit()
    await db.refresh(new_professor)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_professor.id}, expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": new_professor.id,
            "name": new_professor.name,
            "email": new_professor.email,
            "department": new_professor.department,
            "role": new_professor.role,
        },
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Professor = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        department=current_user.department,
        role=current_user.role,
    )
