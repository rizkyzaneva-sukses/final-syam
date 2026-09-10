from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, Token, UserOut
from ..auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    return Token(access_token=create_access_token(user))

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
