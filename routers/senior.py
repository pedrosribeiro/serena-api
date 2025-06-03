from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.compartment import Compartment
from models.device import Device
from models.dispenser import Dispenser
from models.senior import Senior
from models.user import User
from models.usersenior import UserSenior
from schemas.senior import SeniorCreate, SeniorRead

router = APIRouter()


@router.get("/by_device/{device_id}", dependencies=[Depends(get_current_user)])
def get_senior_by_device(device_id: str, db: Session = Depends(get_session)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    senior = device.senior
    if not senior:
        raise HTTPException(status_code=404, detail="Senior not found")
    return {"senior_id": senior.id}


@router.post(
    "/",
    response_model=SeniorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_senior(
    senior: SeniorCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Verifica se o device_id já está associado a outro Senior
    existing_device = db.query(Device).filter(Device.id == senior.device_id).first()
    if existing_device:
        raise HTTPException(
            status_code=400, detail="Device ID already assigned to another Senior."
        )

    # Cria o Senior
    db_senior = Senior(
        name=senior.name,
        birth_date=senior.birth_date,
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(db_senior)
    db.commit()
    db.refresh(db_senior)

    # Relaciona User com Senior
    user_senior = UserSenior(user_id=current_user.id, senior_id=db_senior.id)
    db.add(user_senior)
    db.commit()

    # Cria o Device
    device = Device(id=senior.device_id, senior_id=db_senior.id, status="active")
    db.add(device)
    db.commit()
    db.refresh(device)

    # Cria o Dispenser
    dispenser = Dispenser(device_id=device.id)
    db.add(dispenser)
    db.commit()
    db.refresh(dispenser)

    # Cria os Compartments
    for i in range(14):
        compartment = Compartment(
            dispenser_id=dispenser.id, medication_id="", quantity=0
        )
        db.add(compartment)
    db.commit()

    # Retorna o Senior com o device_id preenchido
    return {
        "id": db_senior.id,
        "name": db_senior.name,
        "birth_date": db_senior.birth_date,
        "created_at": db_senior.created_at,
        "device_id": device.id,
    }


@router.get(
    "/", response_model=List[SeniorRead], dependencies=[Depends(get_current_user)]
)
def list_seniors(db: Session = Depends(get_session)):
    seniors = db.query(Senior).all()
    # Para cada senior, buscar o device_id correspondente
    result = []
    for senior in seniors:
        device = db.query(Device).filter(Device.senior_id == senior.id).first()
        result.append(
            {
                "id": senior.id,
                "name": senior.name,
                "birth_date": senior.birth_date,
                "created_at": senior.created_at,
                "device_id": device.id if device else None,
            }
        )
    return result


@router.get(
    "/{senior_id}", response_model=SeniorRead, dependencies=[Depends(get_current_user)]
)
def get_senior(senior_id: str, db: Session = Depends(get_session)):
    senior = db.query(Senior).filter(Senior.id == senior_id).first()
    if not senior:
        raise HTTPException(status_code=404, detail="Senior not found")
    device = db.query(Device).filter(Device.senior_id == senior.id).first()
    return {
        "id": senior.id,
        "name": senior.name,
        "birth_date": senior.birth_date,
        "created_at": senior.created_at,
        "device_id": device.id if device else None,
    }


@router.put(
    "/{senior_id}", response_model=SeniorRead, dependencies=[Depends(get_current_user)]
)
def update_senior(
    senior_id: str, senior: SeniorCreate, db: Session = Depends(get_session)
):
    db_senior = db.query(Senior).filter(Senior.id == senior_id).first()
    if not db_senior:
        raise HTTPException(status_code=404, detail="Senior not found")
    for key, value in senior.dict().items():
        setattr(db_senior, key, value)
    db.commit()
    db.refresh(db_senior)
    device = db.query(Device).filter(Device.senior_id == db_senior.id).first()
    return {
        "id": db_senior.id,
        "name": db_senior.name,
        "birth_date": db_senior.birth_date,
        "created_at": db_senior.created_at,
        "device_id": device.id if device else None,
    }


@router.delete(
    "/{senior_id}", status_code=204, dependencies=[Depends(get_current_user)]
)
def delete_senior(senior_id: str, db: Session = Depends(get_session)):
    senior = db.query(Senior).filter(Senior.id == senior_id).first()
    if not senior:
        raise HTTPException(status_code=404, detail="Senior not found")
    db.delete(senior)
    db.commit()
    return
