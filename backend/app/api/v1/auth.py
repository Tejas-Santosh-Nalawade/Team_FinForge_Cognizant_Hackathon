"""Small JWT authentication boundary for the local FinForge workspace."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.db.models import User
from backend.db.session import get_db


router = APIRouter(prefix="/auth", tags=["authentication"])
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


def _serialize_user(user: User) -> Dict[str, str]:
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role}


def _create_access_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": user.id, "email": user.email, "role": user.role, "exp": expires_at},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def _ensure_local_demo_user(db: Session) -> User:
    user = db.query(User).filter(User.email == settings.DEMO_USER_EMAIL.lower()).first()
    if user:
        return user
    user = User(
        email=settings.DEMO_USER_EMAIL.lower(),
        full_name="Alex Morgan",
        role="Audit Manager",
        password_hash=password_context.hash(settings.DEMO_USER_PASSWORD),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login")
def login(payload: LoginPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Authenticate the seeded local user and issue a time-limited access token."""
    _ensure_local_demo_user(db)
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not password_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user.last_login_at = datetime.utcnow()
    db.commit()
    return {
        "access_token": _create_access_token(user),
        "token_type": "bearer",
        "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "user": _serialize_user(user),
    }


@router.get("/me")
def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return _serialize_user(user)
