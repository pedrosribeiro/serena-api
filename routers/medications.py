from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_session
from models.medication import Medication
from models.user import User
from routers.prescriptions import get_current_user
from schemas.prescription import MedicationCreate, MedicationRead
from utils.jwt import decode_access_token

router = APIRouter()


def get_medication_or_404(db, medication_id, user_id):
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    # Verifica se pertence ao usuário via prescription
    if (
        hasattr(medication, "prescription")
        and medication.prescription.user_id != user_id
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
    return medication


@router.post("/", response_model=MedicationRead)
def create_medication(
    medication: MedicationCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_med = Medication(**medication.dict())
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med


@router.get("/", response_model=List[MedicationRead])
def list_medications(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
):
    # Lista todos os medicamentos das prescrições do usuário
    return (
        db.query(Medication)
        .join("prescription")
        .filter_by(user_id=current_user.id)
        .all()
    )


@router.get("/{medication_id}", response_model=MedicationRead)
def get_medication(
    medication_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    medication = get_medication_or_404(db, medication_id, current_user.id)
    return medication


@router.delete("/{medication_id}", status_code=204)
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    medication = get_medication_or_404(db, medication_id, current_user.id)
    db.delete(medication)
    db.commit()
    return


@router.put("/{medication_id}", response_model=MedicationRead)
def update_medication(
    medication_id: int,
    medication: MedicationCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_med = get_medication_or_404(db, medication_id, current_user.id)
    db_med.name = medication.name
    db_med.dosage = medication.dosage
    db.commit()
    db.refresh(db_med)
    return db_med
