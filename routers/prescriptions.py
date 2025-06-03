from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.medication import Medication
from models.prescription import Prescription
from models.user import User
from schemas.prescription import PrescriptionCreate, PrescriptionRead
from utils.jwt import decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post(
    "/", response_model=PrescriptionRead, dependencies=[Depends(get_current_user)]
)
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


@router.get(
    "/", response_model=List[PrescriptionRead], dependencies=[Depends(get_current_user)]
)
def list_prescriptions(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
):
    return db.query(Prescription).filter(Prescription.user_id == current_user.id).all()


@router.get(
    "/{prescription_id}",
    response_model=PrescriptionRead,
    dependencies=[Depends(get_current_user)],
)
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


@router.delete(
    "/{prescription_id}", status_code=204, dependencies=[Depends(get_current_user)]
)
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


@router.put(
    "/{prescription_id}",
    response_model=PrescriptionRead,
    dependencies=[Depends(get_current_user)],
)
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


@router.get("/by_device/{device_id}", dependencies=[Depends(get_current_user)])
def get_valid_prescriptions_by_device(
    device_id: str, db: Session = Depends(get_session)
):
    from datetime import date

    from models.device import Device
    from models.prescription import Prescription
    from models.senior import Senior

    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    senior = device.senior
    if not senior:
        raise HTTPException(status_code=404, detail="Senior not found")
    today = date.today()
    prescriptions = (
        db.query(Prescription)
        .filter(Prescription.senior_id == senior.id, Prescription.end_date >= today)
        .all()
    )
    return prescriptions


@router.get("/by_senior/{senior_id}", dependencies=[Depends(get_current_user)])
def get_prescriptions_by_senior(senior_id: str, db: Session = Depends(get_session)):
    from models.prescription import Prescription

    prescriptions = (
        db.query(Prescription).filter(Prescription.senior_id == senior_id).all()
    )
    return prescriptions
