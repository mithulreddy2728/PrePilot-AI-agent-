"""Company-specific AI interview routes."""

import json
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.company import Company
from ..models.interview import InterviewSession, InterviewMessage
from ..models.activity import UserActivity
from ..utils.dependencies import get_current_user
from ..services.ai_service import generate_interview_question, evaluate_answer

router = APIRouter(prefix="/api/interview", tags=["Interview"])


class AnswerRequest(BaseModel):
    answer: str


class StartInterviewRequest(BaseModel):
    company_id: int


@router.get("/companies")
def list_companies(db: Session = Depends(get_db)):
    """List all available companies for interview practice."""
    companies = db.query(Company).filter(Company.is_active == True).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "logo_url": c.logo_url,
            "description": c.description,
            "industry": c.industry,
            "difficulty": c.difficulty,
        }
        for c in companies
    ]


@router.post("/start")
async def start_interview(
    req: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new AI interview session for a company."""
    company = db.query(Company).filter(Company.id == req.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create session
    session = InterviewSession(
        user_id=current_user.id,
        company_id=company.id,
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate first question
    q_data = await generate_interview_question(company.name)

    msg = InterviewMessage(
        session_id=session.id,
        role="interviewer",
        content=q_data.get("question", "Tell me about yourself."),
        question_type=q_data.get("type", "behavioral"),
        order_num=1,
    )
    db.add(msg)
    session.question_count = 1
    db.commit()

    # Track activity
    activity = UserActivity(
        user_id=current_user.id,
        activity_type="interview",
        date=date.today(),
        details=f"Started interview with {company.name}",
    )
    db.add(activity)
    db.commit()

    return {
        "session_id": session.id,
        "company": company.name,
        "question": msg.content,
        "question_type": msg.question_type,
        "question_number": 1,
        "hints": q_data.get("hints", []),
    }


@router.post("/{session_id}/answer")
async def submit_answer(
    session_id: int,
    req: AnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit an answer and get AI evaluation + next question."""
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is not active")

    company = db.query(Company).filter(Company.id == session.company_id).first()

    # Get last question
    last_q = (
        db.query(InterviewMessage)
        .filter(InterviewMessage.session_id == session_id, InterviewMessage.role == "interviewer")
        .order_by(InterviewMessage.order_num.desc())
        .first()
    )

    # Save candidate answer
    answer_msg = InterviewMessage(
        session_id=session_id,
        role="candidate",
        content=req.answer,
        order_num=last_q.order_num if last_q else 1,
    )
    db.add(answer_msg)

    # Evaluate the answer
    evaluation = await evaluate_answer(
        question=last_q.content if last_q else "",
        answer=req.answer,
        company=company.name,
    )

    answer_msg.ai_feedback = evaluation.get("feedback", "")
    answer_msg.score = evaluation.get("score", 5)

    result = {
        "evaluation": evaluation,
        "question_number": session.question_count,
    }

    # If less than 8 questions, generate next question
    if session.question_count < 8:
        context = f"Previous Q: {last_q.content if last_q else ''}\nCandidate A: {req.answer}"
        q_data = await generate_interview_question(company.name, context=context)

        next_msg = InterviewMessage(
            session_id=session_id,
            role="interviewer",
            content=q_data.get("question", ""),
            question_type=q_data.get("type", "technical"),
            order_num=session.question_count + 1,
        )
        db.add(next_msg)
        session.question_count += 1

        result["next_question"] = next_msg.content
        result["next_question_type"] = next_msg.question_type
        result["hints"] = q_data.get("hints", [])
        result["is_complete"] = False
    else:
        # End session
        session.status = "completed"
        session.ended_at = datetime.utcnow()

        # Calculate average score
        all_answers = (
            db.query(InterviewMessage)
            .filter(InterviewMessage.session_id == session_id, InterviewMessage.role == "candidate")
            .all()
        )
        avg_score = sum(a.score for a in all_answers) / len(all_answers) if all_answers else 0
        session.score = round(avg_score, 1)
        session.feedback = f"Overall score: {session.score}/10. You answered {len(all_answers)} questions."

        # Update user score
        current_user.total_score += int(avg_score * 10)

        result["is_complete"] = True
        result["final_score"] = session.score
        result["final_feedback"] = session.feedback

    db.commit()
    return result


@router.post("/{session_id}/end")
def end_interview(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """End an interview session early."""
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = "completed"
    session.ended_at = datetime.utcnow()

    all_answers = (
        db.query(InterviewMessage)
        .filter(InterviewMessage.session_id == session_id, InterviewMessage.role == "candidate")
        .all()
    )
    avg_score = sum(a.score for a in all_answers) / len(all_answers) if all_answers else 0
    session.score = round(avg_score, 1)
    db.commit()

    return {
        "message": "Interview ended",
        "score": session.score,
        "questions_answered": len(all_answers),
    }


@router.get("/history")
def interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's interview session history."""
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.started_at.desc())
        .all()
    )
    result = []
    for s in sessions:
        company = db.query(Company).filter(Company.id == s.company_id).first()
        result.append({
            "id": s.id,
            "company": company.name if company else "Unknown",
            "company_logo": company.logo_url if company else "",
            "status": s.status,
            "score": s.score,
            "question_count": s.question_count,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "ended_at": s.ended_at.isoformat() if s.ended_at else None,
        })
    return result


@router.get("/{session_id}")
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific interview session."""
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    company = db.query(Company).filter(Company.id == session.company_id).first()
    messages = (
        db.query(InterviewMessage)
        .filter(InterviewMessage.session_id == session_id)
        .order_by(InterviewMessage.order_num, InterviewMessage.id)
        .all()
    )

    return {
        "id": session.id,
        "company": company.name if company else "Unknown",
        "status": session.status,
        "score": session.score,
        "feedback": session.feedback,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "question_type": m.question_type,
                "ai_feedback": m.ai_feedback,
                "score": m.score,
            }
            for m in messages
        ],
    }
