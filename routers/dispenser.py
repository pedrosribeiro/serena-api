from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.compartment import Compartment
from models.device import Device
from models.dispenser import Dispenser
from models.medication import Medication
from schemas.compartment import CompartmentCreate, CompartmentRead, CompartmentUpdate
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


@router.patch("/compartment/{compartment_id}", dependencies=[Depends(get_current_user)])
def update_compartment_quantity(
    compartment_id: str, update: CompartmentUpdate, db: Session = Depends(get_session)
):
    compartment = (
        db.query(Compartment)
        .filter(Compartment.compartment_id == compartment_id)
        .first()
    )
    if not compartment:
        raise HTTPException(status_code=404, detail="Compartment not found")
    compartment.quantity = update.quantity
    db.commit()
    db.refresh(compartment)
    return compartment


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


# CRUD para Compartment
@router.post(
    "/compartment/",
    response_model=CompartmentRead,
    dependencies=[Depends(get_current_user)],
)
def create_compartment(
    compartment: CompartmentCreate, db: Session = Depends(get_session)
):
    db_compartment = Compartment(**compartment.dict())
    db.add(db_compartment)
    db.commit()
    db.refresh(db_compartment)
    return db_compartment


@router.get(
    "/compartment/",
    response_model=List[CompartmentRead],
    dependencies=[Depends(get_current_user)],
)
def list_compartments(db: Session = Depends(get_session)):
    return db.query(Compartment).all()


@router.get(
    "/compartment/{compartment_id}",
    response_model=CompartmentRead,
    dependencies=[Depends(get_current_user)],
)
def get_compartment(compartment_id: str, db: Session = Depends(get_session)):
    compartment = (
        db.query(Compartment)
        .filter(Compartment.compartment_id == compartment_id)
        .first()
    )
    if not compartment:
        raise HTTPException(status_code=404, detail="Compartment not found")
    return compartment


@router.put(
    "/compartment/{compartment_id}",
    response_model=CompartmentRead,
    dependencies=[Depends(get_current_user)],
)
def update_compartment(
    compartment_id: str,
    compartment: CompartmentCreate,
    db: Session = Depends(get_session),
):
    db_compartment = (
        db.query(Compartment)
        .filter(Compartment.compartment_id == compartment_id)
        .first()
    )
    if not db_compartment:
        raise HTTPException(status_code=404, detail="Compartment not found")
    for key, value in compartment.dict().items():
        setattr(db_compartment, key, value)
    db.commit()
    db.refresh(db_compartment)
    return db_compartment


@router.delete(
    "/compartment/{compartment_id}",
    status_code=204,
    dependencies=[Depends(get_current_user)],
)
def delete_compartment(compartment_id: str, db: Session = Depends(get_session)):
    compartment = (
        db.query(Compartment)
        .filter(Compartment.compartment_id == compartment_id)
        .first()
    )
    if not compartment:
        raise HTTPException(status_code=404, detail="Compartment not found")
    db.delete(compartment)
    db.commit()
    return
