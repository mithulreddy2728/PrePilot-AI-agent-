"""Resume model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf or docx
    file_size = Column(Integer, default=0)
    ats_score = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    skills = Column(Text, default="[]")  # JSON array
    missing_skills = Column(Text, default="[]")  # JSON array
    suggestions = Column(Text, default="[]")  # JSON array
    summary = Column(Text, default="")
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
