from datetime import datetime
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
    # Verifica se o senior existe
    from models.senior import Senior

    senior = db.query(Senior).filter(Senior.id == prescription.senior_id).first()
    if not senior:
        raise HTTPException(status_code=404, detail="Senior not found.")
    # Verifica se o medicamento existe
    from models.medication import Medication

    medication = (
        db.query(Medication).filter(Medication.id == prescription.medication_id).first()
    )
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found.")
    # Verifica se o doctor existe e tem role 'doctor'
    from models.user import User as UserModel

    doctor = db.query(UserModel).filter(UserModel.id == prescription.doctor_id).first()
    if not doctor or doctor.role != "doctor":
        raise HTTPException(status_code=404, detail="Doctor not found or not a doctor.")
    # Converte datas ISO string para datetime
    try:
        start_date = (
            prescription.start_date
            if isinstance(prescription.start_date, datetime)
            else datetime.fromisoformat(prescription.start_date)
        )
        end_date = (
            prescription.end_date
            if isinstance(prescription.end_date, datetime)
            else datetime.fromisoformat(prescription.end_date)
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use ISO 8601."
        )
    db_prescription = Prescription(
        senior_id=prescription.senior_id,
        medication_id=prescription.medication_id,
        doctor_id=prescription.doctor_id,
        dosage=prescription.dosage,
        frequency=prescription.frequency,
        start_date=start_date,
        end_date=end_date,
        description=prescription.description,
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    # Monta resposta com medication e doctor
    med = (
        db.query(Medication)
        .filter(Medication.id == db_prescription.medication_id)
        .first()
    )
    medication_data = None
    if med:
        medication_data = {
            "id": med.id,
            "name": med.name,
            "description": med.description,
        }
    doctor = db.query(User).filter(User.id == db_prescription.doctor_id).first()
    doctor_data = None
    if doctor:
        doctor_data = {"id": doctor.id, "name": doctor.name}
    presc_data = {
        **db_prescription.__dict__,
        "medication": medication_data,
        "doctor": doctor_data,
    }
    return PrescriptionRead(**presc_data)


@router.get(
    "/", response_model=List[PrescriptionRead], dependencies=[Depends(get_current_user)]
)
def list_prescriptions(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
):
    prescriptions = db.query(Prescription).all()
    result = []
    for presc in prescriptions:
        med = db.query(Medication).filter(Medication.id == presc.medication_id).first()
        medication_data = None
        if med:
            medication_data = {
                "id": med.id,
                "name": med.name,
                "description": med.description,
            }
        doctor = db.query(User).filter(User.id == presc.doctor_id).first()
        doctor_data = None
        if doctor:
            doctor_data = {"id": doctor.id, "name": doctor.name}
        presc_data = {
            **presc.__dict__,
            "medication": medication_data,
            "doctor": doctor_data,
        }
        result.append(PrescriptionRead(**presc_data))
    return result


@router.get(
    "/{prescription_id}",
    response_model=PrescriptionRead,
    dependencies=[Depends(get_current_user)],
)
def get_prescription(
    prescription_id: str,
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
    prescription_id: str,
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
    prescription_id: str,
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
    prescriptions = (
        db.query(Prescription).filter(Prescription.senior_id == senior_id).all()
    )
    result = []
    for presc in prescriptions:
        med = db.query(Medication).filter(Medication.id == presc.medication_id).first()
        medication_data = None
        if med:
            medication_data = {
                "id": med.id,
                "name": med.name,
                "description": med.description,
            }
        doctor = db.query(User).filter(User.id == presc.doctor_id).first()
        doctor_data = None
        if doctor:
            doctor_data = {"id": doctor.id, "name": doctor.name}
        presc_data = {
            **presc.__dict__,
            "medication": medication_data,
            "doctor": doctor_data,
        }
        result.append(PrescriptionRead(**presc_data))
    return result
