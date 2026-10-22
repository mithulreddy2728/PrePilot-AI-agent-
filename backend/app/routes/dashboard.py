"""Dashboard routes with analytics, heatmap, readiness score, and recommendations."""

import json
from datetime import date, timedelta
from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.user import User
from ..models.resume import Resume
from ..models.interview import InterviewSession
from ..models.coding import Submission, CodingQuestion
from ..models.planner import StudyPlan, StudyTask
from ..models.chat import ChatSession
from ..models.activity import UserActivity
from ..utils.dependencies import get_current_user, get_optional_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive dashboard statistics (supports preview mode for unauthenticated visitors)."""
    total_questions = db.query(CodingQuestion).count()
    if not current_user:
        return {
            "is_preview": True,
            "readiness_score": 72.0,
            "ats_score": 82,
            "interview_count": 3,
            "avg_interview_score": 78.5,
            "coding_solved": 14,
            "unique_solved": 14,
            "total_questions": total_questions or 35,
            "streak_days": 5,
            "total_score": 180,
            "resume": {"count": 1, "latest_score": 82, "rating": "Strong Fit"},
            "interviews": {"count": 3, "avg_score": 78.5, "completed": 3},
            "coding": {"submissions": 20, "passed": 14, "unique_solved": 14, "total_questions": total_questions or 35},
            "study": {"active_plans": 1, "total_tasks": 7, "completed_tasks": 4, "progress": 57},
            "chats": 2,
        }

    uid = current_user.id

    # Resume stats
    resume_count = db.query(Resume).filter(Resume.user_id == uid).count()
    latest_resume = (
        db.query(Resume)
        .filter(Resume.user_id == uid)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    ats_score = latest_resume.ats_score if latest_resume else 0

    # Interview stats
    interview_count = db.query(InterviewSession).filter(InterviewSession.user_id == uid).count()
    completed_interviews = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == uid, InterviewSession.status == "completed")
        .all()
    )
    avg_interview_score = (
        sum(i.score for i in completed_interviews) / len(completed_interviews)
        if completed_interviews
        else 0
    )

    # Coding stats
    total_submissions = db.query(Submission).filter(Submission.user_id == uid).count()
    passed_submissions = (
        db.query(Submission)
        .filter(Submission.user_id == uid, Submission.status == "passed")
        .count()
    )
    unique_solved = (
        db.query(func.count(func.distinct(Submission.question_id)))
        .filter(Submission.user_id == uid, Submission.status == "passed")
        .scalar()
    )
    total_questions = db.query(CodingQuestion).count()

    # Study plan stats
    active_plans = (
        db.query(StudyPlan)
        .filter(StudyPlan.user_id == uid, StudyPlan.is_active == True)
        .count()
    )
    total_tasks = (
        db.query(StudyTask)
        .join(StudyPlan)
        .filter(StudyPlan.user_id == uid)
        .count()
    )
    completed_tasks = (
        db.query(StudyTask)
        .join(StudyPlan)
        .filter(StudyPlan.user_id == uid, StudyTask.is_completed == True)
        .count()
    )

    # Chat sessions
    chat_count = db.query(ChatSession).filter(ChatSession.user_id == uid).count()

    # Calculate readiness score (0-100)
    readiness = min(100, int(
        (ats_score * 0.2) +
        (avg_interview_score * 3) +  # 0-10 -> 0-30
        (min(unique_solved / max(total_questions, 1) * 100, 30)) +
        (min(completed_tasks / max(total_tasks, 1) * 100, 20) if total_tasks > 0 else 0)
    ))

    return {
        "user": {
            "full_name": current_user.full_name,
            "streak_days": current_user.streak_days,
            "total_score": current_user.total_score,
        },
        "readiness_score": readiness,
        "resume": {
            "count": resume_count,
            "latest_ats_score": ats_score,
        },
        "interviews": {
            "total": interview_count,
            "completed": len(completed_interviews),
            "avg_score": round(avg_interview_score, 1),
        },
        "coding": {
            "total_submissions": total_submissions,
            "passed": passed_submissions,
            "unique_solved": unique_solved,
            "total_questions": total_questions,
        },
        "study": {
            "active_plans": active_plans,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "progress": round(completed_tasks / max(total_tasks, 1) * 100),
        },
        "chats": chat_count,
    }


@router.get("/heatmap")
def get_activity_heatmap(
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Get activity heatmap data for the last 365 days."""
    end_date = date.today()
    start_date = end_date - timedelta(days=365)

    if not current_user:
        # Preview heatmap
        return {
            "heatmap": {
                (end_date - timedelta(days=i)).isoformat(): (i % 4) for i in range(14)
            },
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

    activities = (
        db.query(UserActivity)
        .filter(
            UserActivity.user_id == current_user.id,
            UserActivity.date >= start_date,
            UserActivity.date <= end_date,
        )
        .all()
    )

    heatmap = defaultdict(int)
    for a in activities:
        key = a.date.isoformat() if a.date else ""
        heatmap[key] += a.count

    return {
        "heatmap": dict(heatmap),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


@router.get("/charts")
def get_chart_data(
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Get data for Chart.js visualizations."""
    if not current_user:
        return {
            "daily_submissions": [{"date": (date.today() - timedelta(days=i)).isoformat(), "count": 2 + (i % 3)} for i in range(6, -1, -1)],
            "difficulty_distribution": {"easy": 8, "medium": 5, "hard": 1},
            "interview_scores": [
                {"date": (date.today() - timedelta(days=3)).isoformat(), "score": 75},
                {"date": (date.today() - timedelta(days=2)).isoformat(), "score": 82},
                {"date": (date.today() - timedelta(days=1)).isoformat(), "score": 85},
            ],
            "categories": [
                {"name": "DSA & Algorithms", "score": 78},
                {"name": "System Design", "score": 65},
                {"name": "Core CS (OS/DBMS)", "score": 82},
                {"name": "Behavioral (STAR)", "score": 75},
                {"name": "Problem Solving Speed", "score": 70},
            ],
            "task_categories": {"DSA": 4, "System Design": 2, "HR": 1},
        }

    uid = current_user.id

    # Submissions per day (last 7 days)
    daily_submissions = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        count = (
            db.query(Submission)
            .filter(
                Submission.user_id == uid,
                func.date(Submission.submitted_at) == d,
            )
            .count()
        )
        daily_submissions.append({"date": d.isoformat(), "count": count})

    # Difficulty distribution of solved problems
    difficulty_stats = {"easy": 0, "medium": 0, "hard": 0}
    solved = (
        db.query(Submission.question_id)
        .filter(Submission.user_id == uid, Submission.status == "passed")
        .distinct()
        .all()
    )
    for (qid,) in solved:
        q = db.query(CodingQuestion).filter(CodingQuestion.id == qid).first()
        if q:
            difficulty_stats[q.difficulty] = difficulty_stats.get(q.difficulty, 0) + 1

    # Interview scores trend
    interview_scores = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == uid, InterviewSession.status == "completed")
        .order_by(InterviewSession.ended_at)
        .limit(10)
        .all()
    )

    # Category breakdown of study tasks
    task_categories = (
        db.query(StudyTask.category, func.count(StudyTask.id))
        .join(StudyPlan)
        .filter(StudyPlan.user_id == uid)
        .group_by(StudyTask.category)
        .all()
    )

    return {
        "daily_submissions": daily_submissions,
        "difficulty_distribution": difficulty_stats,
        "interview_scores": [
            {"date": s.ended_at.isoformat() if s.ended_at else "", "score": s.score}
            for s in interview_scores
        ],
        "categories": [
            {"name": "DSA & Algorithms", "score": 78},
            {"name": "System Design", "score": 65},
            {"name": "Core CS (OS/DBMS)", "score": 82},
            {"name": "Behavioral (STAR)", "score": 75},
            {"name": "Problem Solving Speed", "score": 70},
        ],
        "task_categories": {cat: count for cat, count in task_categories},
    }


@router.get("/recommendations")
def get_recommendations(
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Get personalized recommendations for the user."""
    if not current_user:
        return {
            "recommendations": [
                {
                    "type": "coding",
                    "priority": "high",
                    "title": "Master Google & Amazon DSA Track",
                    "description": "Practice high-frequency interview questions: Two Sum, LRU Cache, and Maximum Subarray.",
                    "action_view": "coding",
                    "action_text": "Practice Company Questions",
                },
                {
                    "type": "resume",
                    "priority": "medium",
                    "title": "Analyze Resume for ATS Fit",
                    "description": "Check if your resume passes automated filters for Google, Microsoft, and Deloitte.",
                    "action_view": "resume",
                    "action_text": "Upload Resume",
                },
                {
                    "type": "interview",
                    "priority": "high",
                    "title": "Simulate Live AI Interview",
                    "description": "Practice with AI interviewer for Amazon Leadership Principles or Google Problem Solving.",
                    "action_view": "interview",
                    "action_text": "Start AI Mock Interview",
                },
            ]
        }

    uid = current_user.id
    recommendations = []

    # Check resume
    resume = db.query(Resume).filter(Resume.user_id == uid).first()
    if not resume:
        recommendations.append({
            "type": "resume",
            "icon": "fa-file-alt",
            "title": "Upload Your Resume",
            "description": "Get your resume analyzed for ATS compatibility and receive improvement suggestions.",
            "action": "#/resume",
            "priority": "high",
        })
    elif resume.ats_score < 70:
        recommendations.append({
            "type": "resume",
            "icon": "fa-file-alt",
            "title": "Improve Your Resume",
            "description": f"Your ATS score is {resume.ats_score}%. Try implementing the suggestions to improve it.",
            "action": "#/resume",
            "priority": "medium",
        })

    # Check coding
    solved = (
        db.query(func.count(func.distinct(Submission.question_id)))
        .filter(Submission.user_id == uid, Submission.status == "passed")
        .scalar()
    )
    if solved < 5:
        recommendations.append({
            "type": "coding",
            "icon": "fa-code",
            "title": "Practice Coding Problems",
            "description": f"You've solved {solved} problems. Try solving at least 5 to build a strong foundation.",
            "action": "#/coding",
            "priority": "high",
        })

    # Check interviews
    interviews = db.query(InterviewSession).filter(InterviewSession.user_id == uid).count()
    if interviews < 3:
        recommendations.append({
            "type": "interview",
            "icon": "fa-comments",
            "title": "Practice Mock Interviews",
            "description": "Practice with AI interviewers from top companies to build confidence.",
            "action": "#/interview",
            "priority": "high",
        })

    # Check study plan
    plans = db.query(StudyPlan).filter(StudyPlan.user_id == uid, StudyPlan.is_active == True).count()
    if plans == 0:
        recommendations.append({
            "type": "study",
            "icon": "fa-calendar-alt",
            "title": "Create a Study Plan",
            "description": "Generate an AI-powered study roadmap tailored to your goals.",
            "action": "#/planner",
            "priority": "medium",
        })

    # Streak recommendation
    if current_user.streak_days < 3:
        recommendations.append({
            "type": "streak",
            "icon": "fa-fire",
            "title": "Build Your Streak",
            "description": "Practice daily to build a streak and maintain consistency.",
            "action": "#/dashboard",
            "priority": "low",
        })

    return recommendations
