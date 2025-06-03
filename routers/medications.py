from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.medication import Medication
from models.user import User
from routers.prescriptions import get_current_user
from schemas.medication import MedicationCreate, MedicationRead
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


@router.post(
    "/", response_model=MedicationRead, dependencies=[Depends(get_current_user)]
)
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


@router.get(
    "/", response_model=List[MedicationRead], dependencies=[Depends(get_current_user)]
)
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


@router.get(
    "/{medication_id}",
    response_model=MedicationRead,
    dependencies=[Depends(get_current_user)],
)
def get_medication(
    medication_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    medication = get_medication_or_404(db, medication_id, current_user.id)
    return medication


@router.delete(
    "/{medication_id}", status_code=204, dependencies=[Depends(get_current_user)]
)
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    medication = get_medication_or_404(db, medication_id, current_user.id)
    db.delete(medication)
    db.commit()
    return


@router.put(
    "/{medication_id}",
    response_model=MedicationRead,
    dependencies=[Depends(get_current_user)],
)
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


@router.post(
    "/", response_model=MedicationRead, dependencies=[Depends(get_current_user)]
)
def create_medication(medication: MedicationCreate, db: Session = Depends(get_session)):
    db_med = Medication(**medication.dict())
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med


@router.get(
    "/", response_model=List[MedicationRead], dependencies=[Depends(get_current_user)]
)
def list_medications(db: Session = Depends(get_session)):
    return db.query(Medication).all()


@router.get(
    "/{medication_id}",
    response_model=MedicationRead,
    dependencies=[Depends(get_current_user)],
)
def get_medication(medication_id: str, db: Session = Depends(get_session)):
    med = db.query(Medication).filter(Medication.id == medication_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


@router.put(
    "/{medication_id}",
    response_model=MedicationRead,
    dependencies=[Depends(get_current_user)],
)
def update_medication(
    medication_id: str, medication: MedicationCreate, db: Session = Depends(get_session)
):
    db_med = db.query(Medication).filter(Medication.id == medication_id).first()
    if not db_med:
        raise HTTPException(status_code=404, detail="Medication not found")
    for key, value in medication.dict().items():
        setattr(db_med, key, value)
    db.commit()
    db.refresh(db_med)
    return db_med


@router.delete(
    "/{medication_id}", status_code=204, dependencies=[Depends(get_current_user)]
)
def delete_medication(medication_id: str, db: Session = Depends(get_session)):
    med = db.query(Medication).filter(Medication.id == medication_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    db.delete(med)
    db.commit()
    return
