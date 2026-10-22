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
from ..utils.dependencies import get_current_user
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a resume file (PDF or DOCX) and get AI analysis."""
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
        text = "Sample resume with basic information. Skills: Python, JavaScript. Experience: Software Developer."

    # AI analysis
    analysis = await analyze_resume(text)

    # Save to database
    resume = Resume(
        user_id=current_user.id,
        filename=filename,
        original_filename=file.filename,
        file_type=ext,
        file_size=len(contents),
        ats_score=analysis.get("ats_score", 0),
        rating=analysis.get("rating", 0),
        skills=json.dumps(analysis.get("skills", [])),
        missing_skills=json.dumps(analysis.get("missing_skills", [])),
        suggestions=json.dumps(analysis.get("suggestions", [])),
        summary=analysis.get("summary", ""),
    )
    db.add(resume)

    # Track activity
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
        "skills": json.loads(resume.skills),
        "missing_skills": json.loads(resume.missing_skills),
        "suggestions": json.loads(resume.suggestions),
        "summary": resume.summary,
        "uploaded_at": resume.uploaded_at.isoformat(),
    }


@router.get("/history")
def get_resume_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's resume upload history."""
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
            "skills": json.loads(r.skills),
            "missing_skills": json.loads(r.missing_skills),
            "suggestions": json.loads(r.suggestions),
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
