from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_session
from models.symptom import Symptom
from models.user import User
from routers.prescriptions import get_current_user
from schemas.symptom import SymptomCreate, SymptomRead
from utils.jwt import decode_access_token

router = APIRouter()


@router.post("/", response_model=SymptomRead)
def create_symptom(
    symptom: SymptomCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_symptom = Symptom(user_id=current_user.id, **symptom.dict())
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom


@router.get("/", response_model=List[SymptomRead])
def list_symptoms(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
):
    return db.query(Symptom).filter(Symptom.user_id == current_user.id).all()


@router.get("/{symptom_id}", response_model=SymptomRead)
def get_symptom(
    symptom_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    symptom = (
        db.query(Symptom)
        .filter(Symptom.id == symptom_id, Symptom.user_id == current_user.id)
        .first()
    )
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")
    return symptom


@router.delete("/{symptom_id}", status_code=204)
def delete_symptom(
    symptom_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    symptom = (
        db.query(Symptom)
        .filter(Symptom.id == symptom_id, Symptom.user_id == current_user.id)
        .first()
    )
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")
    db.delete(symptom)
    db.commit()
    return


@router.put("/{symptom_id}", response_model=SymptomRead)
def update_symptom(
    symptom_id: int,
    symptom: SymptomCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_symptom = (
        db.query(Symptom)
        .filter(Symptom.id == symptom_id, Symptom.user_id == current_user.id)
        .first()
    )
    if not db_symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")
    db_symptom.name = symptom.name
    db_symptom.description = symptom.description
    db.commit()
    db.refresh(db_symptom)
    return db_symptom
