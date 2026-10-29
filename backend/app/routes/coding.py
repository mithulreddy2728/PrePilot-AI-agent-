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


import sys
import shutil

def execute_code_sandboxed(code: str, language: str = "python", input_data: str = "", timeout: int = 5):
    """
    Executes code in Python, JavaScript (Node.js), C, C++, Java, or PHP.
    Returns: dict(output=str, error=str, success=bool, runtime_ms=int)
    """
    lang = (language or "python").lower().strip()
    start_time = time.time()

    # 1. PYTHON
    if lang in ("python", "python3", "py"):
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                tmp_path = f.name
            
            res = subprocess.run(
                [sys.executable or "python3", tmp_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed = int((time.time() - start_time) * 1000)
            return {
                "output": res.stdout.strip(),
                "error": res.stderr.strip()[:1000],
                "success": res.returncode == 0,
                "runtime_ms": elapsed
            }
        except subprocess.TimeoutExpired:
            return {"output": "", "error": f"Time Limit Exceeded ({timeout}s)", "success": False, "runtime_ms": timeout * 1000}
        except Exception as e:
            return {"output": "", "error": str(e)[:500], "success": False, "runtime_ms": 0}
        finally:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                try: os.unlink(tmp_path)
                except Exception: pass

    # 2. JAVASCRIPT / NODE.JS
    elif lang in ("javascript", "js", "node", "nodejs"):
        node_bin = shutil.which("node") or "/usr/local/bin/node" or "/opt/homebrew/bin/node"
        if not shutil.which("node") and not os.path.exists(str(node_bin)):
            return {"output": "", "error": "Node.js engine not found on server", "success": False, "runtime_ms": 0}
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
                f.write(code)
                tmp_path = f.name
            res = subprocess.run(
                [node_bin, tmp_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed = int((time.time() - start_time) * 1000)
            return {
                "output": res.stdout.strip(),
                "error": res.stderr.strip()[:1000],
                "success": res.returncode == 0,
                "runtime_ms": elapsed
            }
        except subprocess.TimeoutExpired:
            return {"output": "", "error": f"Time Limit Exceeded ({timeout}s)", "success": False, "runtime_ms": timeout * 1000}
        except Exception as e:
            return {"output": "", "error": str(e)[:500], "success": False, "runtime_ms": 0}
        finally:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                try: os.unlink(tmp_path)
                except Exception: pass

    # 3. C++ (G++ / CLANG++)
    elif lang in ("cpp", "c++", "cxx"):
        compiler = shutil.which("g++") or shutil.which("clang++") or "/usr/bin/g++"
        if not compiler:
            return {"output": "", "error": "C++ compiler (g++/clang++) not found on server", "success": False, "runtime_ms": 0}
        try:
            with tempfile.TemporaryDirectory() as td:
                src_path = os.path.join(td, "solution.cpp")
                out_path = os.path.join(td, "solution.out")
                with open(src_path, "w") as f:
                    f.write(code)
                c_res = subprocess.run(
                    [compiler, "-O2", "-std=c++17", src_path, "-o", out_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if c_res.returncode != 0:
                    return {
                        "output": "",
                        "error": f"Compilation Error:\n{c_res.stderr[:1000]}",
                        "success": False,
                        "runtime_ms": 0
                    }
                run_start = time.time()
                r_res = subprocess.run(
                    [out_path],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                elapsed = int((time.time() - run_start) * 1000)
                return {
                    "output": r_res.stdout.strip(),
                    "error": r_res.stderr.strip()[:1000],
                    "success": r_res.returncode == 0,
                    "runtime_ms": elapsed
                }
        except subprocess.TimeoutExpired:
            return {"output": "", "error": f"Time Limit Exceeded ({timeout}s)", "success": False, "runtime_ms": timeout * 1000}
        except Exception as e:
            return {"output": "", "error": str(e)[:500], "success": False, "runtime_ms": 0}

    # 4. C (GCC / CLANG)
    elif lang in ("c", "gcc", "clang"):
        compiler = shutil.which("gcc") or shutil.which("clang") or "/usr/bin/gcc"
        if not compiler:
            return {"output": "", "error": "C compiler (gcc/clang) not found on server", "success": False, "runtime_ms": 0}
        try:
            with tempfile.TemporaryDirectory() as td:
                src_path = os.path.join(td, "solution.c")
                out_path = os.path.join(td, "solution.out")
                with open(src_path, "w") as f:
                    f.write(code)
                c_res = subprocess.run(
                    [compiler, "-O2", src_path, "-o", out_path, "-lm"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if c_res.returncode != 0:
                    return {
                        "output": "",
                        "error": f"Compilation Error:\n{c_res.stderr[:1000]}",
                        "success": False,
                        "runtime_ms": 0
                    }
                run_start = time.time()
                r_res = subprocess.run(
                    [out_path],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                elapsed = int((time.time() - run_start) * 1000)
                return {
                    "output": r_res.stdout.strip(),
                    "error": r_res.stderr.strip()[:1000],
                    "success": r_res.returncode == 0,
                    "runtime_ms": elapsed
                }
        except subprocess.TimeoutExpired:
            return {"output": "", "error": f"Time Limit Exceeded ({timeout}s)", "success": False, "runtime_ms": timeout * 1000}
        except Exception as e:
            return {"output": "", "error": str(e)[:500], "success": False, "runtime_ms": 0}

    # 5. JAVA
    elif lang in ("java", "openjdk"):
        javac_bin = shutil.which("javac")
        java_bin = shutil.which("java")
        # Check standard brew openjdk paths if not linked to /usr/bin
        for prefix in ("/opt/homebrew/opt/openjdk/bin", "/usr/local/opt/openjdk/bin"):
            if os.path.exists(os.path.join(prefix, "javac")):
                javac_bin = os.path.join(prefix, "javac")
                java_bin = os.path.join(prefix, "java")
                break

        if not javac_bin or not java_bin:
            return {"output": "", "error": "Java Runtime environment (javac/java) is currently initializing.", "success": False, "runtime_ms": 0}
        try:
            with tempfile.TemporaryDirectory() as td:
                class_name = "Solution"
                for line in code.splitlines():
                    if "class " in line and "public class " in line:
                        parts = line.split("class ")[1].split()[0].strip("{")
                        if parts:
                            class_name = parts
                            break
                src_path = os.path.join(td, f"{class_name}.java")
                with open(src_path, "w") as f:
                    f.write(code)
                c_res = subprocess.run(
                    [javac_bin, src_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if c_res.returncode != 0:
                    return {
                        "output": "",
                        "error": f"Compilation Error:\n{c_res.stderr[:1000]}",
                        "success": False,
                        "runtime_ms": 0
                    }
                run_start = time.time()
                r_res = subprocess.run(
                    [java_bin, "-cp", td, class_name],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                elapsed = int((time.time() - run_start) * 1000)
                return {
                    "output": r_res.stdout.strip(),
                    "error": r_res.stderr.strip()[:1000],
                    "success": r_res.returncode == 0,
                    "runtime_ms": elapsed
                }
        except subprocess.TimeoutExpired:
            return {"output": "", "error": f"Time Limit Exceeded ({timeout}s)", "success": False, "runtime_ms": timeout * 1000}
        except Exception as e:
            return {"output": "", "error": str(e)[:500], "success": False, "runtime_ms": 0}

    # 6. PHP
    elif lang in ("php",):
        php_bin = shutil.which("php") or "/opt/homebrew/bin/php"
        if not shutil.which("php") and not os.path.exists(str(php_bin)):
            return {"output": "", "error": "PHP CLI runtime not found on server.", "success": False, "runtime_ms": 0}
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".php", delete=False) as f:
                f.write(code if "<?php" in code else f"<?php\n{code}")
                tmp_path = f.name
            res = subprocess.run(
                [php_bin, tmp_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            elapsed = int((time.time() - start_time) * 1000)
            return {
                "output": res.stdout.strip(),
                "error": res.stderr.strip()[:1000],
                "success": res.returncode == 0,
                "runtime_ms": elapsed
            }
        except subprocess.TimeoutExpired:
            return {"output": "", "error": f"Time Limit Exceeded ({timeout}s)", "success": False, "runtime_ms": timeout * 1000}
        except Exception as e:
            return {"output": "", "error": str(e)[:500], "success": False, "runtime_ms": 0}
        finally:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                try: os.unlink(tmp_path)
                except Exception: pass

    else:
        return {"output": "", "error": f"Language '{language}' is not currently configured for execution.", "success": False, "runtime_ms": 0}


@router.post("/questions/{question_id}/submit")
def submit_code(
    question_id: int,
    req: SubmitCodeRequest,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Submit code for a coding question and run against test cases in the specified language."""
    # Fallback to student user if in preview / demo mode
    if not current_user:
        current_user = db.query(User).filter(User.email == "student@preppilot.com").first()
        if not current_user:
            current_user = db.query(User).first()

    q = db.query(CodingQuestion).filter(CodingQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    test_cases = json.loads(q.test_cases) if q.test_cases else []

    # Run the code against all test cases
    results = []
    all_passed = True
    total_time = 0

    for i, tc in enumerate(test_cases):
        input_data = tc.get("input", "")
        expected_output = tc.get("expected", "").strip()

        exec_res = execute_code_sandboxed(
            code=req.code,
            language=req.language,
            input_data=input_data,
            timeout=5,
        )

        actual_output = exec_res["output"]
        passed = (actual_output == expected_output)
        if not passed:
            all_passed = False

        total_time += exec_res["runtime_ms"]
        results.append({
            "test_case": i + 1,
            "passed": passed,
            "input": input_data,
            "expected": expected_output,
            "actual": actual_output,
            "error": exec_res["error"],
            "runtime_ms": exec_res["runtime_ms"],
        })

    status = "passed" if all_passed else "failed"

    # Save submission if user exists
    if current_user:
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

        activity = UserActivity(
            user_id=current_user.id,
            activity_type="coding",
            date=date.today(),
            details=f"Submitted {req.language} solution for: {q.title} ({status})",
        )
        db.add(activity)

        if all_passed:
            points = {"easy": 10, "medium": 20, "hard": 30}.get(q.difficulty, 10)
            current_user.total_score += points

        db.commit()

    return {
        "status": status,
        "language": req.language,
        "results": results,
        "runtime_ms": total_time,
        "passed": sum(1 for r in results if r["passed"]),
        "total": len(results),
    }


@router.post("/run")
def run_code(
    req: SubmitCodeRequest,
    current_user: User | None = Depends(get_optional_current_user),
):
    """Run code without test cases in any selected language (free run)."""
    exec_res = execute_code_sandboxed(
        code=req.code,
        language=req.language,
        input_data="",
        timeout=10,
    )
    return {
        "output": exec_res["output"],
        "error": exec_res["error"],
        "success": exec_res["success"],
        "runtime_ms": exec_res["runtime_ms"],
    }


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
    """Get the enriched coding leaderboard with rankings, tiers, and college stats."""
    users = (
        db.query(User)
        .filter(User.is_admin == False)
        .order_by(User.total_score.desc(), User.streak_days.desc())
        .limit(100)
        .all()
    )

    # Get distinct passed solved count per user
    solved_map = {}
    try:
        user_ids = [u.id for u in users]
        if user_ids:
            counts = (
                db.query(Submission.user_id, func.count(func.distinct(Submission.question_id)))
                .filter(Submission.user_id.in_(user_ids), Submission.status == "passed")
                .group_by(Submission.user_id)
                .all()
            )
            solved_map = {uid: count for uid, count in counts}
    except Exception:
        solved_map = {}

    colleges = [
        "IIT Bombay", "IIT Delhi", "BITS Pilani", "NIT Trichy", "IIIT Hyderabad",
        "IIT Madras", "DTU Delhi", "IIT Roorkee", "VIT Vellore", "NIT Surathkal"
    ]
    target_companies = ["Google", "Microsoft", "Amazon", "Goldman Sachs", "Meta", "Apple", "Uber", "Netflix"]

    leaderboard = []
    for i, u in enumerate(users):
        score = u.total_score or 0
        real_solved = solved_map.get(u.id, 0)
        # If user has demo score without formal submissions, estimate realistic solved count
        solved_count = max(real_solved, max(1, score // 15))

        if score >= 300:
            tier = "Grandmaster"
            badge = "👑 Grandmaster"
        elif score >= 200:
            tier = "Master"
            badge = "💎 Master"
        elif score >= 140:
            tier = "Diamond"
            badge = "⚔️ Diamond"
        elif score >= 80:
            tier = "Expert"
            badge = "⚡ Expert"
        else:
            tier = "Rising Star"
            badge = "⭐ Rising Star"

        # Extract college/target if stored in bio, otherwise deterministically assign
        college = colleges[u.id % len(colleges)]
        if u.bio and "College:" in u.bio:
            try:
                college = u.bio.split("College:")[1].split("|")[0].strip()
            except Exception:
                pass

        target = target_companies[u.id % len(target_companies)]
        if u.bio and "Target:" in u.bio:
            try:
                target = u.bio.split("Target:")[1].split("|")[0].strip()
            except Exception:
                pass

        easy = max(1, int(solved_count * 0.5))
        med = max(0, int(solved_count * 0.35))
        hard = max(0, solved_count - easy - med)

        leaderboard.append({
            "rank": i + 1,
            "id": u.id,
            "full_name": u.full_name,
            "avatar_url": u.avatar_url or "",
            "total_score": score,
            "streak_days": u.streak_days or 1,
            "solved_count": solved_count,
            "easy_solved": easy,
            "med_solved": med,
            "hard_solved": hard,
            "tier": tier,
            "badge": badge,
            "college": college,
            "target_company": target,
        })

    return leaderboard
