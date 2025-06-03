from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.symptom import Symptom
from models.user import User
from routers.prescriptions import get_current_user
from schemas.symptom import SymptomCreate, SymptomRead
from utils.jwt import decode_access_token

router = APIRouter()


@router.post("/", response_model=SymptomRead, dependencies=[Depends(get_current_user)])
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


@router.get(
    "/", response_model=List[SymptomRead], dependencies=[Depends(get_current_user)]
)
def list_symptoms(
    db: Session = Depends(get_session), current_user: User = Depends(get_current_user)
):
    return db.query(Symptom).filter(Symptom.user_id == current_user.id).all()


@router.get(
    "/{symptom_id}",
    response_model=SymptomRead,
    dependencies=[Depends(get_current_user)],
)
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


@router.delete(
    "/{symptom_id}", status_code=204, dependencies=[Depends(get_current_user)]
)
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


@router.put(
    "/{symptom_id}",
    response_model=SymptomRead,
    dependencies=[Depends(get_current_user)],
)
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


@router.get("/by_senior/{senior_id}", dependencies=[Depends(get_current_user)])
def get_symptoms_by_senior(senior_id: str, db: Session = Depends(get_session)):
    from models.symptom import Symptom

    symptoms = db.query(Symptom).filter(Symptom.senior_id == senior_id).all()
    return symptoms


@router.post("/by_device/{device_id}", dependencies=[Depends(get_current_user)])
def create_symptom_by_device(
    device_id: str, symptom: SymptomCreate, db: Session = Depends(get_session)
):
    from models.device import Device
    from models.senior import Senior
    from models.symptom import Symptom

    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    senior = device.senior
    if not senior:
        raise HTTPException(status_code=404, detail="Senior not found")
    db_symptom = Symptom(senior_id=senior.id, **symptom.dict())
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom


@router.post("/", response_model=SymptomRead)
def create_symptom(symptom: SymptomCreate, db: Session = Depends(get_session)):
    db_symptom = Symptom(**symptom.dict())
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom


@router.get("/", response_model=List[SymptomRead])
def list_symptoms(db: Session = Depends(get_session)):
    return db.query(Symptom).all()


@router.get("/{symptom_id}", response_model=SymptomRead)
def get_symptom(symptom_id: str, db: Session = Depends(get_session)):
    symptom = db.query(Symptom).filter(Symptom.id == symptom_id).first()
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")
    return symptom


@router.put("/{symptom_id}", response_model=SymptomRead)
def update_symptom(
    symptom_id: str, symptom: SymptomCreate, db: Session = Depends(get_session)
):
    db_symptom = db.query(Symptom).filter(Symptom.id == symptom_id).first()
    if not db_symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")
    for key, value in symptom.dict().items():
        setattr(db_symptom, key, value)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom


@router.delete("/{symptom_id}", status_code=204)
def delete_symptom(symptom_id: str, db: Session = Depends(get_session)):
    symptom = db.query(Symptom).filter(Symptom.id == symptom_id).first()
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")
    db.delete(symptom)
    db.commit()
    return
