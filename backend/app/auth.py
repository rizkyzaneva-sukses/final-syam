import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import User, Role
from .auth_models import AuthSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must be at most 72 UTF-8 bytes")
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    if len(password.encode("utf-8")) > 72:
        return False
    try:
        return pwd_context.verify(password, hashed)
    except (ValueError, TypeError):
        return False


def token_digest(token_id: str) -> str:
    return hashlib.sha256(token_id.encode()).hexdigest()


def create_access_token(user: User, db: Session) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    token_id = secrets.token_urlsafe(32)
    db.add(AuthSession(token_id=token_digest(token_id), user_id=user.id, expires_at=exp.replace(tzinfo=None)))
    db.flush()
    return jwt.encode({"sub": str(user.id), "jti": token_id, "exp": exp}, settings.secret_key, algorithm="HS256")


def current_session(token: str, db: Session) -> AuthSession:
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"], options={"require": ["exp", "sub", "jti"]})
        user_id = int(payload.get("sub"))
        token_id = payload.get("jti")
        if not isinstance(token_id, str):
            raise error
        session = db.get(AuthSession, token_digest(token_id))
    except (PyJWTError, TypeError, ValueError):
        raise error
    if not session or session.user_id != user_id or session.revoked_at or session.expires_at <= datetime.utcnow():
        raise error
    return session


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    session = current_session(token, db)
    user = db.get(User, session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


def require_roles(*roles: Role):
    def dep(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Role not allowed")
        return user
    return dep
