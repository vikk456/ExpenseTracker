from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.models import User
from auth.utils import hash_password, verify_password, create_access_token, get_current_user
from schemas.models import UserCreate, UserResponse, Token, UserLogin

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(req: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(new_user.id)
    return {"access_token": access_token}

@router.post("/login", response_model=Token)
async def login(req: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    access_token = create_access_token(user.id)
    return {"access_token": access_token}

@router.get("/me", response_model=UserResponse)
async def get_me(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user

@router.post("/logout")
async def logout():
    return {"message": "Logout successful"}