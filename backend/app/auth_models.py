from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from .database import Base


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    token_id = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    id = Column(Integer, primary_key=True)
    key = Column(String(64), nullable=False, index=True)
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
