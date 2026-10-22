"""FastAPI dependencies for authentication and database access."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from .security import decode_access_token

security_scheme = HTTPBearer()
security_scheme_optional = HTTPBearer(auto_error=False)


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme_optional),
    db: Session = Depends(get_db),
) -> User | None:
    """Extract current user if token is provided, otherwise return None."""
    if not credentials or not credentials.credentials:
        return None
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the current user from the JWT bearer token."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user has admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
