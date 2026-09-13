import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..auth_models import AuthSession, LoginAttempt
from ..config import settings
from ..schemas import LoginRequest, Token, UserOut
from ..auth import verify_password, hash_password, create_access_token, get_current_user, current_session, oauth2_scheme
from ..audit import log_audit

router = APIRouter(prefix="/auth", tags=["auth"])
_DUMMY_HASH = hash_password("dummy-password-for-login-timing")


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(seconds=settings.login_window_seconds)
    # Account key avoids proxy bypasses; never trust client X-Forwarded-For.
    email = payload.email.strip().lower()
    key = hashlib.sha256(email.encode()).hexdigest()
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int(key[:15], 16)})
    db.query(LoginAttempt).filter(LoginAttempt.attempted_at < cutoff).delete(synchronize_session=False)
    if db.query(LoginAttempt).filter(LoginAttempt.key == key, LoginAttempt.attempted_at >= cutoff).count() >= settings.login_max_attempts:
        db.commit()
        raise HTTPException(429, "Terlalu banyak percobaan login. Coba lagi nanti.", headers={"Retry-After": str(settings.login_window_seconds)})
    db.add(LoginAttempt(key=key))
    db.commit()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    valid = verify_password(payload.password, user.password_hash if user else _DUMMY_HASH)
    if not user or not user.is_active or not valid:
        raise HTTPException(401, "Email atau password salah")
    token = create_access_token(user, db)
    db.query(LoginAttempt).filter(LoginAttempt.key == key).delete(synchronize_session=False)
    db.query(AuthSession).filter(AuthSession.expires_at < datetime.utcnow()).delete(synchronize_session=False)
    db.commit()
    response.headers["Cache-Control"] = "no-store"
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/logout", status_code=204)
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    session = current_session(token, db)
    session.revoked_at = datetime.utcnow()
    log_audit(db, db.get(User, session.user_id), "LOGOUT", "users", session.user_id)
    db.commit()
    return Response(status_code=204)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=72)


@router.post("/change-password", status_code=204)
def change_password(payload: PasswordChange, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(400, "Password saat ini salah")
    if len(payload.new_password.encode("utf-8")) > 72:
        raise HTTPException(422, "Password maksimal 72 UTF-8 bytes")
    user.password_hash = hash_password(payload.new_password)
    log_audit(db, user, "PASSWORD_CHANGED", "users", user.id, "All sessions revoked")
    db.query(AuthSession).filter(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).update({"revoked_at": datetime.utcnow()}, synchronize_session=False)
    db.commit()
    return Response(status_code=204)
