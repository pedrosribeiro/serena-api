from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.user import User
from schemas.user import UserCreate, UserRead

router = APIRouter()


@router.post("/", response_model=UserRead, dependencies=[Depends(get_current_user)])
def create_user(user: UserCreate, db: Session = Depends(get_session)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get(
    "/", response_model=List[UserRead], dependencies=[Depends(get_current_user)]
)
def list_users(db: Session = Depends(get_session)):
    return db.query(User).all()


@router.get(
    "/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_user)]
)
def get_user(user_id: str, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put(
    "/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_user)]
)
def update_user(user_id: str, user: UserCreate, db: Session = Depends(get_session)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=204, dependencies=[Depends(get_current_user)])
def delete_user(user_id: str, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return
