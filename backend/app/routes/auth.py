"""Authentication routes: register, login, logout, verify email, forgot/reset password."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    MessageResponse,
)
from ..utils.security import hash_password, verify_password, create_access_token, generate_token
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=MessageResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    verification_token = generate_token()
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        verification_token=verification_token,
        is_verified=True,  # Auto-verify for local dev; set to False in production with SMTP
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return MessageResponse(
        message="Registration successful! You can now log in.",
        detail=f"Verification token (dev): {verification_token}",
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Log in and receive a JWT access token."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    # Update streak
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if user.last_active_date != today:
        yesterday = (datetime.utcnow().date()).isoformat()
        if user.last_active_date and user.last_active_date >= yesterday:
            user.streak_days += 1
        else:
            user.streak_days = 1
        user.last_active_date = today
        db.commit()

    token = create_access_token(data={"sub": user.id, "email": user.email})

    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "is_verified": user.is_verified,
            "streak_days": user.streak_days,
            "total_score": user.total_score,
            "avatar_url": user.avatar_url,
        },
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "is_admin": current_user.is_admin,
        "is_verified": current_user.is_verified,
        "streak_days": current_user.streak_days,
        "total_score": current_user.total_score,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.put("/profile")
def update_profile(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    if "full_name" in data:
        current_user.full_name = data["full_name"]
    if "bio" in data:
        current_user.bio = data["bio"]
    if "avatar_url" in data:
        current_user.avatar_url = data["avatar_url"]
    db.commit()
    return {"message": "Profile updated successfully"}


@router.get("/verify/{token}", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address using the verification token."""
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return MessageResponse(message="Email verified successfully! You can now log in.")


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request a password reset token."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Don't reveal whether the email exists
        return MessageResponse(message="If the email exists, a reset link has been sent.")

    reset_token = generate_token()
    user.reset_token = reset_token
    db.commit()

    return MessageResponse(
        message="If the email exists, a reset link has been sent.",
        detail=f"Reset token (dev): {reset_token}",
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using the reset token."""
    user = db.query(User).filter(User.reset_token == req.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user.password_hash = hash_password(req.new_password)
    user.reset_token = None
    db.commit()

    return MessageResponse(message="Password reset successfully! You can now log in.")
