"""Coding question, submission, and bookmark models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from ..database import Base


class CodingQuestion(Base):
    __tablename__ = "coding_questions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), default="easy")  # easy, medium, hard
    category = Column(String(100), default="general")
    test_cases = Column(Text, default="[]")  # JSON array
    solution = Column(Text, default="")
    constraints = Column(Text, default="")
    examples = Column(Text, default="[]")  # JSON array
    starter_code = Column(Text, default="")
    acceptance_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    submissions = relationship("Submission", back_populates="question")
    bookmarks = relationship("Bookmark", back_populates="question")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("coding_questions.id"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(20), default="python")
    status = Column(String(20), default="pending")  # pending, passed, failed, error
    output = Column(Text, default="")
    runtime_ms = Column(Integer, default=0)
    test_results = Column(Text, default="[]")  # JSON array
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="submissions")
    question = relationship("CodingQuestion", back_populates="submissions")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("coding_questions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    question = relationship("CodingQuestion", back_populates="bookmarks")
