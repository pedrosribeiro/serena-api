from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.device import Device
from models.dispenser import Dispenser
from schemas.dispenser import DispenserCreate, DispenserRead

router = APIRouter()


@router.get("/by_device/{device_id}", dependencies=[Depends(get_current_user)])
def get_dispenser_content(device_id: str, db: Session = Depends(get_session)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    dispenser = device.dispenser
    if not dispenser:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    compartments = [
        {
            "compartment_id": c.compartment_id,
            "medication_name": c.medication.name if c.medication else None,
            "quantity": c.quantity,
        }
        for c in dispenser.compartments
    ]
    return compartments


@router.get("/by_senior/{senior_id}", dependencies=[Depends(get_current_user)])
def get_dispenser_by_senior(senior_id: str, db: Session = Depends(get_session)):
    from models.senior import Senior

    senior = db.query(Senior).filter(Senior.id == senior_id).first()
    if not senior:
        raise HTTPException(status_code=404, detail="Senior not found")
    device = senior.device
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    dispenser = device.dispenser
    if not dispenser:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    compartments = [
        {
            "compartment_id": c.compartment_id,
            "medication_name": c.medication.name if c.medication else None,
            "quantity": c.quantity,
        }
        for c in dispenser.compartments
    ]
    return compartments


@router.post(
    "/", response_model=DispenserRead, dependencies=[Depends(get_current_user)]
)
def create_dispenser(dispenser: DispenserCreate, db: Session = Depends(get_session)):
    db_dispenser = Dispenser(**dispenser.dict())
    db.add(db_dispenser)
    db.commit()
    db.refresh(db_dispenser)
    return db_dispenser


@router.get(
    "/", response_model=List[DispenserRead], dependencies=[Depends(get_current_user)]
)
def list_dispensers(db: Session = Depends(get_session)):
    return db.query(Dispenser).all()


@router.get(
    "/{dispenser_id}",
    response_model=DispenserRead,
    dependencies=[Depends(get_current_user)],
)
def get_dispenser(dispenser_id: str, db: Session = Depends(get_session)):
    dispenser = db.query(Dispenser).filter(Dispenser.id == dispenser_id).first()
    if not dispenser:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    return dispenser


@router.put(
    "/{dispenser_id}",
    response_model=DispenserRead,
    dependencies=[Depends(get_current_user)],
)
def update_dispenser(
    dispenser_id: str, dispenser: DispenserCreate, db: Session = Depends(get_session)
):
    db_dispenser = db.query(Dispenser).filter(Dispenser.id == dispenser_id).first()
    if not db_dispenser:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    for key, value in dispenser.dict().items():
        setattr(db_dispenser, key, value)
    db.commit()
    db.refresh(db_dispenser)
    return db_dispenser


@router.delete(
    "/{dispenser_id}", status_code=204, dependencies=[Depends(get_current_user)]
)
def delete_dispenser(dispenser_id: str, db: Session = Depends(get_session)):
    dispenser = db.query(Dispenser).filter(Dispenser.id == dispenser_id).first()
    if not dispenser:
        raise HTTPException(status_code=404, detail="Dispenser not found")
    db.delete(dispenser)
    db.commit()
    return
