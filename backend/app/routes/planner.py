"""Study planner routes: plans, tasks, roadmap generation, calendar."""

import json
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.planner import StudyPlan, StudyTask
from ..models.activity import UserActivity
from ..utils.dependencies import get_current_user
from ..services.ai_service import generate_study_plan

router = APIRouter(prefix="/api/planner", tags=["Study Planner"])


class CreatePlanRequest(BaseModel):
    title: str = ""
    preferences: str = ""  # e.g. "focus on DSA, weak at DP"


class CreateTaskRequest(BaseModel):
    plan_id: int
    title: str
    description: str = ""
    date: str = ""  # YYYY-MM-DD
    category: str = "general"
    priority: str = "medium"


class UpdateTaskRequest(BaseModel):
    is_completed: bool


@router.post("/generate")
async def generate_plan(
    req: CreatePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate an AI-powered weekly study roadmap."""
    plan_data = await generate_study_plan(req.preferences or "balanced placement preparation")

    # Create the plan
    start = date.today()
    end = start + timedelta(days=6)
    plan = StudyPlan(
        user_id=current_user.id,
        title=plan_data.get("title", req.title or "Weekly Study Plan"),
        description=req.preferences,
        start_date=start,
        end_date=end,
        is_active=True,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    # Create tasks from AI response
    tasks_data = plan_data.get("tasks", [])
    created_tasks = []
    for t in tasks_data:
        day_offset = t.get("day", 1) - 1
        task_date = start + timedelta(days=day_offset)
        task = StudyTask(
            plan_id=plan.id,
            title=t.get("title", "Study"),
            description=t.get("description", ""),
            date=task_date,
            category=t.get("category", "general"),
            priority="medium",
        )
        db.add(task)
        created_tasks.append(task)

    # Track activity
    activity = UserActivity(
        user_id=current_user.id,
        activity_type="study",
        date=date.today(),
        details=f"Generated study plan: {plan.title}",
    )
    db.add(activity)
    db.commit()

    return {
        "id": plan.id,
        "title": plan.title,
        "start_date": plan.start_date.isoformat(),
        "end_date": plan.end_date.isoformat(),
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "date": t.date.isoformat() if t.date else None,
                "category": t.category,
                "is_completed": t.is_completed,
            }
            for t in created_tasks
        ],
    }


@router.get("/plans")
def get_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all study plans for the current user."""
    plans = (
        db.query(StudyPlan)
        .filter(StudyPlan.user_id == current_user.id)
        .order_by(StudyPlan.created_at.desc())
        .all()
    )
    result = []
    for p in plans:
        tasks = db.query(StudyTask).filter(StudyTask.plan_id == p.id).all()
        completed = sum(1 for t in tasks if t.is_completed)
        result.append({
            "id": p.id,
            "title": p.title,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "is_active": p.is_active,
            "total_tasks": len(tasks),
            "completed_tasks": completed,
            "progress": round(completed / len(tasks) * 100) if tasks else 0,
        })
    return result


@router.get("/plans/{plan_id}")
def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific study plan with all tasks."""
    plan = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == plan_id, StudyPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    tasks = (
        db.query(StudyTask)
        .filter(StudyTask.plan_id == plan.id)
        .order_by(StudyTask.date, StudyTask.id)
        .all()
    )

    return {
        "id": plan.id,
        "title": plan.title,
        "description": plan.description,
        "start_date": plan.start_date.isoformat() if plan.start_date else None,
        "end_date": plan.end_date.isoformat() if plan.end_date else None,
        "is_active": plan.is_active,
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "date": t.date.isoformat() if t.date else None,
                "category": t.category,
                "priority": t.priority,
                "is_completed": t.is_completed,
            }
            for t in tasks
        ],
    }


@router.post("/tasks")
def create_task(
    req: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually add a task to a plan."""
    plan = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == req.plan_id, StudyPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    task_date = date.fromisoformat(req.date) if req.date else date.today()
    task = StudyTask(
        plan_id=plan.id,
        title=req.title,
        description=req.description,
        date=task_date,
        category=req.category,
        priority=req.priority,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "date": task.date.isoformat() if task.date else None,
        "category": task.category,
        "is_completed": task.is_completed,
    }


@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    req: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a task as completed or incomplete."""
    task = db.query(StudyTask).filter(StudyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify the plan belongs to the user
    plan = db.query(StudyPlan).filter(StudyPlan.id == task.plan_id, StudyPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=403, detail="Access denied")

    task.is_completed = req.is_completed

    if req.is_completed:
        current_user.total_score += 5
        activity = UserActivity(
            user_id=current_user.id,
            activity_type="study",
            date=date.today(),
            details=f"Completed task: {task.title}",
        )
        db.add(activity)

    db.commit()
    return {"message": "Task updated", "is_completed": task.is_completed}


@router.get("/calendar")
def get_calendar(
    month: int = None,
    year: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get calendar view of tasks for a given month."""
    today = date.today()
    m = month or today.month
    y = year or today.year

    start = date(y, m, 1)
    if m == 12:
        end = date(y + 1, 1, 1)
    else:
        end = date(y, m + 1, 1)

    tasks = (
        db.query(StudyTask)
        .join(StudyPlan)
        .filter(
            StudyPlan.user_id == current_user.id,
            StudyTask.date >= start,
            StudyTask.date < end,
        )
        .order_by(StudyTask.date)
        .all()
    )

    # Group by date
    calendar = {}
    for t in tasks:
        key = t.date.isoformat() if t.date else "unknown"
        if key not in calendar:
            calendar[key] = []
        calendar[key].append({
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "is_completed": t.is_completed,
        })

    return {"month": m, "year": y, "calendar": calendar}
