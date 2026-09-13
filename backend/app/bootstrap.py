"""Operator-only user provisioning. Passwords are prompted, never command-line arguments."""
import argparse
import getpass
from datetime import datetime
from sqlalchemy import func
from email_validator import validate_email, EmailNotValidError
from .database import SessionLocal
from .models import User, Role
from .auth_models import AuthSession
from .auth import hash_password
from .audit import log_audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create-user", "reset-password", "deactivate-user"])
    parser.add_argument("--email", required=True)
    parser.add_argument("--name")
    parser.add_argument("--role", choices=[r.value for r in Role], default=Role.CEO.value)
    args = parser.parse_args()
    try:
        email = validate_email(args.email, check_deliverability=False, test_environment=True).normalized.lower()
    except EmailNotValidError as exc:
        parser.error(str(exc))
    with SessionLocal() as db:
        user = db.query(User).filter(func.lower(User.email) == email).first()
        if args.action == "create-user" and user:
            parser.error("User already exists; use reset-password")
        if args.action != "create-user" and not user:
            parser.error("User not found")
        if args.action == "deactivate-user":
            user.is_active = False
        else:
            password = getpass.getpass("New password (12-72 UTF-8 bytes): ")
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm or len(password) < 12 or len(password.encode("utf-8")) > 72:
                parser.error("Passwords must match, have at least 12 characters and at most 72 UTF-8 bytes")
            if args.action == "create-user":
                if not args.name:
                    parser.error("--name is required for create-user")
                user = User(email=email, name=args.name, role=Role(args.role), password_hash=hash_password(password))
                db.add(user)
                db.flush()
            else:
                user.password_hash = hash_password(password)
        db.query(AuthSession).filter(AuthSession.user_id == user.id).update({"revoked_at": datetime.utcnow()}, synchronize_session=False)
        log_audit(db, None, args.action.upper().replace("-", "_"), "users", user.id, "Operator CLI; sessions revoked")
        db.commit()
    print("Account updated successfully.")


if __name__ == "__main__":
    main()
