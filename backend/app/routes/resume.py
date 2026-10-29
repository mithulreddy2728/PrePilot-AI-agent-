"""Resume upload and AI analysis routes."""

import os
import json
import uuid
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.resume import Resume
from ..models.activity import UserActivity
from ..utils.dependencies import get_current_user, get_optional_current_user
from ..services.ai_service import analyze_resume
from ..config import settings

router = APIRouter(prefix="/api/resume", tags=["Resume"])


def _extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF text: {e}"


def _extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"Error extracting DOCX text: {e}"


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Upload a resume file (PDF or DOCX) and get AI analysis."""
    # Fallback to student demo user if in preview / guest mode
    if not current_user:
        current_user = db.query(User).filter(User.email == "student@preppilot.com").first()
        if not current_user:
            current_user = db.query(User).first()

    # Validate file type
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 5MB")

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text
    if ext == "pdf":
        text = _extract_text_from_pdf(file_path)
    else:
        text = _extract_text_from_docx(file_path)

    if not text or len(text) < 50:
        text = "Sample resume with basic information. Skills: Python, JavaScript, Algorithms, SQL, Docker. Experience: Software Engineer Intern."

    # AI analysis
    analysis = await analyze_resume(text)

    skills_list = analysis.get("skills", ["Python", "Algorithms", "SQL", "Git", "Data Structures"])
    missing_list = analysis.get("missing_skills", ["Docker", "Kubernetes", "System Design Metrics"])
    suggestions_list = analysis.get("suggestions", [
        "Include quantifiable project metrics (e.g. 40% latency reduction)",
        "Highlight your top DSA and competitive programming ratings",
        "Add links to your live projects and GitHub repository"
    ])

    user_id = current_user.id if current_user else 1

    # Save to database
    resume = Resume(
        user_id=user_id,
        filename=filename,
        original_filename=file.filename,
        file_type=ext,
        file_size=len(contents),
        ats_score=analysis.get("ats_score", 82),
        rating=analysis.get("rating", 4.2),
        skills=json.dumps(skills_list),
        missing_skills=json.dumps(missing_list),
        suggestions=json.dumps(suggestions_list),
        summary=analysis.get("summary", "Resume demonstrates good foundation for software engineering roles."),
    )
    db.add(resume)

    # Track activity
    if current_user:
        activity = UserActivity(
            user_id=current_user.id,
            activity_type="resume",
            date=date.today(),
            details=f"Uploaded resume: {file.filename}",
        )
        db.add(activity)
    
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "filename": resume.original_filename,
        "ats_score": resume.ats_score,
        "rating": resume.rating,
        "skills": skills_list,
        "extracted_skills": skills_list,
        "missing_skills": missing_list,
        "suggestions": suggestions_list,
        "summary": resume.summary,
        "uploaded_at": resume.uploaded_at.isoformat(),
    }


@router.get("/history")
def get_resume_history(
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Get user's resume upload history."""
    if not current_user:
        current_user = db.query(User).filter(User.email == "student@preppilot.com").first() or db.query(User).first()
    
    if not current_user:
        return []

    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "filename": r.original_filename,
            "ats_score": r.ats_score,
            "rating": r.rating,
            "skills": json.loads(r.skills) if r.skills else [],
            "extracted_skills": json.loads(r.skills) if r.skills else [],
            "missing_skills": json.loads(r.missing_skills) if r.missing_skills else [],
            "suggestions": json.loads(r.suggestions) if r.suggestions else [],
            "summary": r.summary,
            "uploaded_at": r.uploaded_at.isoformat(),
        }
        for r in resumes
    ]


@router.get("/{resume_id}")
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific resume analysis."""
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return {
        "id": resume.id,
        "filename": resume.original_filename,
        "ats_score": resume.ats_score,
        "rating": resume.rating,
        "skills": json.loads(resume.skills),
        "missing_skills": json.loads(resume.missing_skills),
        "suggestions": json.loads(resume.suggestions),
        "summary": resume.summary,
        "uploaded_at": resume.uploaded_at.isoformat(),
    }
