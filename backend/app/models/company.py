"""Company model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    logo_url = Column(String(500), default="")
    description = Column(Text, default="")
    industry = Column(String(100), default="")
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    interview_focus = Column(Text, default="")  # JSON: areas of focus
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview_sessions = relationship("InterviewSession", back_populates="company")
