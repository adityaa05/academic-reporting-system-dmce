# backend/app/models/domain.py

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Text,
    DateTime,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
from app.schemas.payload import OperationalDomain


class Professor(Base):
    """
    Represents a faculty member within the department hierarchy.
    """

    __tablename__ = "professors"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    department = Column(String, nullable=False, default="IT")
    role = Column(String, nullable=False, default="FACULTY")

    # Self-referential foreign key to establish the HOD reporting structure
    reports_to_id = Column(String, ForeignKey("professors.id"), nullable=True)

    reports = relationship("DailyReport", back_populates="professor")


class DailyReport(Base):
    """
    Stores the executive summary and metadata for a finalized daily submission.
    """

    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    professor_id = Column(
        String, ForeignKey("professors.id"), nullable=False, index=True
    )
    date_submitted = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    executive_summary = Column(Text, nullable=False)

    professor = relationship("Professor", back_populates="reports")
    tasks = relationship("Task", back_populates="report", cascade="all, delete-orphan")


class Task(Base):
    """
    Stores individual completed activities linked to a specific daily report.
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(
        Integer, ForeignKey("daily_reports.id"), nullable=False, index=True
    )
    domain = Column(SQLEnum(OperationalDomain), nullable=False)
    action = Column(String, nullable=False)
    metric = Column(String, nullable=True)

    report = relationship("DailyReport", back_populates="tasks")
