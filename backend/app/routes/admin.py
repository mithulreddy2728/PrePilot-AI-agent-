"""Admin dashboard routes for managing users, companies, questions, and analytics."""

import json
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.user import User
from ..models.company import Company
from ..models.interview import InterviewSession
from ..models.coding import CodingQuestion, Submission
from ..models.resume import Resume
from ..models.activity import UserActivity
from ..utils.dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class CompanyUpdate(BaseModel):
    name: str = ""
    description: str = ""
    industry: str = ""
    difficulty: str = ""
    is_active: bool = True


class QuestionCreate(BaseModel):
    title: str
    description: str
    difficulty: str = "easy"
    category: str = "general"
    test_cases: str = "[]"
    solution: str = ""
    constraints: str = ""
    examples: str = "[]"
    starter_code: str = ""


@router.get("/stats")
def admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get admin analytics overview."""
    total_users = db.query(User).count()
    new_users_week = (
        db.query(User)
        .filter(User.created_at >= date.today() - timedelta(days=7))
        .count()
    )
    total_resumes = db.query(Resume).count()
    total_interviews = db.query(InterviewSession).count()
    total_submissions = db.query(Submission).count()
    total_questions = db.query(CodingQuestion).count()

    # Users registered per day (last 7 days)
    daily_signups = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        count = db.query(User).filter(func.date(User.created_at) == d).count()
        daily_signups.append({"date": d.isoformat(), "count": count})

    return {
        "total_users": total_users,
        "new_users_week": new_users_week,
        "total_resumes": total_resumes,
        "total_interviews": total_interviews,
        "total_submissions": total_submissions,
        "total_questions": total_questions,
        "daily_signups": daily_signups,
    }


@router.get("/users")
def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all users."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_admin": u.is_admin,
            "is_verified": u.is_verified,
            "total_score": u.total_score,
            "streak_days": u.streak_days,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot delete admin user")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.email} deleted"}


@router.get("/companies")
def admin_list_companies(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all companies (admin view)."""
    companies = db.query(Company).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "industry": c.industry,
            "difficulty": c.difficulty,
            "is_active": c.is_active,
            "interview_count": db.query(InterviewSession).filter(InterviewSession.company_id == c.id).count(),
        }
        for c in companies
    ]


@router.put("/companies/{company_id}")
def update_company(
    company_id: int,
    data: CompanyUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update company details."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if data.name:
        company.name = data.name
    if data.description:
        company.description = data.description
    if data.industry:
        company.industry = data.industry
    if data.difficulty:
        company.difficulty = data.difficulty
    company.is_active = data.is_active
    db.commit()
    return {"message": "Company updated"}


@router.get("/questions")
def admin_list_questions(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all coding questions (admin view)."""
    questions = db.query(CodingQuestion).order_by(CodingQuestion.id).all()
    return [
        {
            "id": q.id,
            "title": q.title,
            "difficulty": q.difficulty,
            "category": q.category,
            "acceptance_rate": q.acceptance_rate,
            "submission_count": db.query(Submission).filter(Submission.question_id == q.id).count(),
        }
        for q in questions
    ]


@router.post("/questions")
def create_question(
    data: QuestionCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new coding question."""
    q = CodingQuestion(
        title=data.title,
        description=data.description,
        difficulty=data.difficulty,
        category=data.category,
        test_cases=data.test_cases,
        solution=data.solution,
        constraints=data.constraints,
        examples=data.examples,
        starter_code=data.starter_code,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"id": q.id, "message": "Question created"}


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a coding question."""
    q = db.query(CodingQuestion).filter(CodingQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return {"message": "Question deleted"}
