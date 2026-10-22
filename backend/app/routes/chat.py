"""AI mentor chat routes with multiple modes."""

import json
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.chat import ChatSession
from ..models.activity import UserActivity
from ..utils.dependencies import get_current_user
from ..services.ai_service import chat_with_mentor

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])


class ChatRequest(BaseModel):
    message: str
    mode: str = "placement"  # placement, resume, interview, career


class CreateSessionRequest(BaseModel):
    mode: str = "placement"
    title: str = ""


@router.post("/send")
async def send_message(
    req: ChatRequest,
    session_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message to the AI mentor and get a response."""
    # Get or create session
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Find active session for this mode or create new
        session = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == current_user.id, ChatSession.mode == req.mode)
            .order_by(ChatSession.updated_at.desc())
            .first()
        )
        if not session:
            session = ChatSession(
                user_id=current_user.id,
                mode=req.mode,
                title=f"{req.mode.title()} Chat",
            )
            db.add(session)
            db.commit()
            db.refresh(session)

    # Parse existing messages
    messages = json.loads(session.messages) if session.messages else []

    # Get AI response
    ai_response = await chat_with_mentor(req.mode, messages, req.message)

    # Append messages
    now = datetime.utcnow().isoformat()
    messages.append({"role": "user", "content": req.message, "timestamp": now})
    messages.append({"role": "assistant", "content": ai_response, "timestamp": now})

    session.messages = json.dumps(messages)
    session.updated_at = datetime.utcnow()

    # Update title from first message if not set
    if session.title in ("New Chat", f"{req.mode.title()} Chat") and len(messages) == 2:
        session.title = req.message[:50] + ("..." if len(req.message) > 50 else "")

    # Track activity
    activity = UserActivity(
        user_id=current_user.id,
        activity_type="chat",
        date=date.today(),
        details=f"Chat in {req.mode} mode",
    )
    db.add(activity)
    db.commit()

    return {
        "session_id": session.id,
        "response": ai_response,
        "mode": session.mode,
    }


@router.get("/sessions")
def get_sessions(
    mode: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's chat sessions."""
    query = db.query(ChatSession).filter(ChatSession.user_id == current_user.id)
    if mode:
        query = query.filter(ChatSession.mode == mode)

    sessions = query.order_by(ChatSession.updated_at.desc()).all()
    return [
        {
            "id": s.id,
            "mode": s.mode,
            "title": s.title,
            "message_count": len(json.loads(s.messages)) if s.messages else 0,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific chat session with messages."""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": session.id,
        "mode": session.mode,
        "title": session.title,
        "messages": json.loads(session.messages) if session.messages else [],
        "created_at": session.created_at.isoformat(),
    }


@router.post("/sessions")
def create_session(
    req: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new chat session."""
    session = ChatSession(
        user_id=current_user.id,
        mode=req.mode,
        title=req.title or f"{req.mode.title()} Chat",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "id": session.id,
        "mode": session.mode,
        "title": session.title,
    }


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a chat session."""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()
    return {"message": "Session deleted"}
