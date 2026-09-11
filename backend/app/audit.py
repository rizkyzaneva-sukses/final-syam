"""Simple audit logging — records CRUD operations to audit_logs table."""
from datetime import datetime
from sqlalchemy.orm import Session
from . import models


def log_audit(db: Session, user, action: str, entity: str, entity_id: int = None, detail: str = None):
    """Write an audit log entry. Call this after successful commit."""
    try:
        entry = models.AuditLog(
            user_id=user.id if user else None,
            action=action,
            entity=entity,
            entity_id=entity_id,
            detail=detail,
        )
        db.add(entry)
        db.flush()  # don't commit — caller handles transaction
    except Exception:
        pass  # never break business logic for audit failures
