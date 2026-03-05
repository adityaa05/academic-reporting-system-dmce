# backend/app/api/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.domain import Professor

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Professor:
    """
    Dependency to extract and validate the current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    professor_id: str = payload.get("sub")
    if professor_id is None:
        raise credentials_exception

    # Fetch user from database
    result = await db.execute(select(Professor).where(Professor.id == professor_id))
    professor = result.scalar_one_or_none()

    if professor is None:
        raise credentials_exception

    return professor


async def get_current_hod(
    current_user: Professor = Depends(get_current_user),
) -> Professor:
    """
    Dependency to ensure the current user is an HOD.
    """
    if current_user.role != "HOD":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HODs can access this resource",
        )
    return current_user
