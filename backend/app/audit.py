"""Audit entries participate in the caller's business transaction."""
from sqlalchemy.orm import Session
from . import models


def log_audit(db: Session, user, action: str, entity: str, entity_id: int = None, detail: str = None):
    entry = models.AuditLog(user_id=user.id if user else None, action=action,
        entity=entity, entity_id=entity_id, detail=detail)
    db.add(entry)
    return entry
