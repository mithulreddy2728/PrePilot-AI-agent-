"""Coding practice routes: questions, submissions, bookmarks, leaderboard."""

import json
import time
import subprocess
import tempfile
import os
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.user import User
from ..models.coding import CodingQuestion, Submission, Bookmark
from ..models.activity import UserActivity
from ..utils.dependencies import get_current_user, get_optional_current_user

router = APIRouter(prefix="/api/coding", tags=["Coding"])


class SubmitCodeRequest(BaseModel):
    code: str
    language: str = "python"


class BookmarkRequest(BaseModel):
    question_id: int


@router.get("/questions")
def list_questions(
    difficulty: str = Query(None),
    category: str = Query(None),
    company: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """List coding questions with optional filtering by difficulty, category, and company."""
    query = db.query(CodingQuestion)
    if difficulty:
        query = query.filter(CodingQuestion.difficulty == difficulty)
    if category:
        query = query.filter(CodingQuestion.category == category)
    if company and company.lower() != "all":
        query = query.filter(CodingQuestion.company.ilike(f"%{company}%"))

    total = query.count()
    questions = query.offset((page - 1) * limit).limit(limit).all()

    # Get user's submission status for each question if logged in
    submitted_ids = set()
    bookmarked_ids = set()
    if current_user:
        submitted_ids = set(
            r[0]
            for r in db.query(Submission.question_id)
            .filter(Submission.user_id == current_user.id, Submission.status == "passed")
            .all()
        )
        bookmarked_ids = set(
            r[0]
            for r in db.query(Bookmark.question_id)
            .filter(Bookmark.user_id == current_user.id)
            .all()
        )

    return {
        "total": total,
        "page": page,
        "questions": [
            {
                "id": q.id,
                "title": q.title,
                "difficulty": q.difficulty,
                "category": q.category,
                "company": getattr(q, "company", "General") or "General",
                "acceptance_rate": q.acceptance_rate,
                "solved": q.id in submitted_ids,
                "bookmarked": q.id in bookmarked_ids,
            }
            for q in questions
        ],
    }


@router.get("/questions/{question_id}")
def get_question(
    question_id: int,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific coding question with details."""
    q = db.query(CodingQuestion).filter(CodingQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    return {
        "id": q.id,
        "title": q.title,
        "description": q.description,
        "difficulty": q.difficulty,
        "category": q.category,
        "company": getattr(q, "company", "General") or "General",
        "constraints": q.constraints,
        "examples": json.loads(q.examples) if q.examples else [],
        "starter_code": q.starter_code,
    }


@router.post("/questions/{question_id}/submit")
def submit_code(
    question_id: int,
    req: SubmitCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit code for a coding question and run against test cases."""
    q = db.query(CodingQuestion).filter(CodingQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    test_cases = json.loads(q.test_cases) if q.test_cases else []

    # Run the code in a sandboxed subprocess
    results = []
    all_passed = True
    total_time = 0

    for i, tc in enumerate(test_cases):
        input_data = tc.get("input", "")
        expected_output = tc.get("expected", "").strip()

        # Create a temporary file with the code
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(req.code)
                tmp_path = f.name

            start_time = time.time()
            result = subprocess.run(
                ["python3", tmp_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5,
            )
            elapsed = int((time.time() - start_time) * 1000)
            total_time += elapsed

            actual_output = result.stdout.strip()
            passed = actual_output == expected_output

            if not passed:
                all_passed = False

            results.append({
                "test_case": i + 1,
                "passed": passed,
                "expected": expected_output,
                "actual": actual_output,
                "error": result.stderr[:500] if result.stderr else "",
                "runtime_ms": elapsed,
            })
        except subprocess.TimeoutExpired:
            all_passed = False
            results.append({
                "test_case": i + 1,
                "passed": False,
                "error": "Time Limit Exceeded (5s)",
                "runtime_ms": 5000,
            })
        except Exception as e:
            all_passed = False
            results.append({
                "test_case": i + 1,
                "passed": False,
                "error": str(e)[:500],
                "runtime_ms": 0,
            })
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    status = "passed" if all_passed else "failed"

    # Save submission
    submission = Submission(
        user_id=current_user.id,
        question_id=question_id,
        code=req.code,
        language=req.language,
        status=status,
        output=json.dumps(results),
        runtime_ms=total_time,
        test_results=json.dumps(results),
    )
    db.add(submission)

    # Track activity
    activity = UserActivity(
        user_id=current_user.id,
        activity_type="coding",
        date=date.today(),
        details=f"Submitted solution for: {q.title} ({status})",
    )
    db.add(activity)

    # Update score if passed
    if all_passed:
        points = {"easy": 10, "medium": 20, "hard": 30}.get(q.difficulty, 10)
        current_user.total_score += points

    db.commit()

    return {
        "status": status,
        "results": results,
        "runtime_ms": total_time,
        "passed": sum(1 for r in results if r["passed"]),
        "total": len(results),
    }


@router.post("/run")
def run_code(
    req: SubmitCodeRequest,
    current_user: User = Depends(get_current_user),
):
    """Run code without test cases (free run)."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(req.code)
            tmp_path = f.name

        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        os.unlink(tmp_path)

        return {
            "output": result.stdout[:5000],
            "error": result.stderr[:5000],
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Time Limit Exceeded (10s)", "success": False}
    except Exception as e:
        return {"output": "", "error": str(e), "success": False}


@router.post("/bookmark")
def toggle_bookmark(
    req: BookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle bookmark on a coding question."""
    existing = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id, Bookmark.question_id == req.question_id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"bookmarked": False}
    else:
        bookmark = Bookmark(user_id=current_user.id, question_id=req.question_id)
        db.add(bookmark)
        db.commit()
        return {"bookmarked": True}


@router.get("/bookmarks")
def get_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's bookmarked questions."""
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id)
        .all()
    )
    question_ids = [b.question_id for b in bookmarks]
    questions = db.query(CodingQuestion).filter(CodingQuestion.id.in_(question_ids)).all()
    return [
        {
            "id": q.id,
            "title": q.title,
            "difficulty": q.difficulty,
            "category": q.category,
        }
        for q in questions
    ]


@router.get("/submissions")
def get_submissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's submission history."""
    submissions = (
        db.query(Submission)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.submitted_at.desc())
        .limit(50)
        .all()
    )
    result = []
    for s in submissions:
        q = db.query(CodingQuestion).filter(CodingQuestion.id == s.question_id).first()
        result.append({
            "id": s.id,
            "question_title": q.title if q else "Unknown",
            "question_id": s.question_id,
            "status": s.status,
            "language": s.language,
            "runtime_ms": s.runtime_ms,
            "submitted_at": s.submitted_at.isoformat(),
        })
    return result


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    """Get the coding leaderboard."""
    users = (
        db.query(User)
        .filter(User.is_admin == False)
        .order_by(User.total_score.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "rank": i + 1,
            "full_name": u.full_name,
            "avatar_url": u.avatar_url,
            "total_score": u.total_score,
            "streak_days": u.streak_days,
        }
        for i, u in enumerate(users)
    ]
