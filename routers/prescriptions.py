from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_session
from models.medication import Medication
from models.prescription import Prescription
from schemas.prescription import PrescriptionCreate, PrescriptionRead
from utils.jwt import decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

from database import SessionLocal

# Helper para obter o usuário autenticado
from models.user import User


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/", response_model=PrescriptionRead)
def create_prescription(
    prescription: PrescriptionCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_prescription = Prescription(
        user_id=current_user.id, description=prescription.description
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    # Adiciona medicamentos se houver
    for med in prescription.medications:
        db_med = Medication(
            prescription_id=db_prescription.id, name=med.name, dosage=med.dosage
        )
        db.add(db_med)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription


@router.get("/", response_model=List[PrescriptionRead])
def list_prescriptions(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
):
    return db.query(Prescription).filter(Prescription.user_id == current_user.id).all()


@router.get("/{prescription_id}", response_model=PrescriptionRead)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    prescription = (
        db.query(Prescription)
        .filter(
            Prescription.id == prescription_id, Prescription.user_id == current_user.id
        )
        .first()
    )
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription


@router.delete("/{prescription_id}", status_code=204)
def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    prescription = (
        db.query(Prescription)
        .filter(
            Prescription.id == prescription_id, Prescription.user_id == current_user.id
        )
        .first()
    )
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db.delete(prescription)
    db.commit()
    return


@router.put("/{prescription_id}", response_model=PrescriptionRead)
def update_prescription(
    prescription_id: int,
    prescription: PrescriptionCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_prescription = (
        db.query(Prescription)
        .filter(
            Prescription.id == prescription_id, Prescription.user_id == current_user.id
        )
        .first()
    )
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db_prescription.description = prescription.description
    db.commit()
    db.refresh(db_prescription)
    return db_prescription
