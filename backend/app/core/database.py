# backend/app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Initialize the asynchronous SQLAlchemy engine
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Configure the session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for all ORM models to inherit from
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency generator yielding database sessions.
    Ensures sessions are closed safely after request completion.
    """
    async with AsyncSessionLocal() as session:
        yield session
