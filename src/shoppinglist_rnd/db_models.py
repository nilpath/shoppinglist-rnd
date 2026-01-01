"""SQLAlchemy ORM models for database persistence."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TaskStatus(str, enum.Enum):
    """Status of an import task."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImportTask(Base):
    """Tracks the status of recipe import tasks."""

    __tablename__ = "import_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String(2048), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    recipe_id = Column(String(36), ForeignKey("recipes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    recipe = relationship("RecipeDB", back_populates="import_task")


class RecipeDB(Base):
    """Persisted recipe data."""

    __tablename__ = "recipes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(2048), nullable=False)
    image = Column(String(2048), nullable=True)
    level_of_difficulty = Column(String(20), default="unknown")
    time = Column(Integer, nullable=True)  # in minutes
    portion = Column(Integer, nullable=True)
    tags = Column(JSON, default=list)  # Stored as JSON array
    ingredients = Column(JSON, default=list)  # Stored as JSON array of objects
    steps = Column(JSON, default=list)  # Stored as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    import_task = relationship("ImportTask", back_populates="recipe", uselist=False)
