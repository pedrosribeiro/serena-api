from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.compartment import Compartment
from models.device import Device
from models.dispenser import Dispenser

router = APIRouter()


def get_dispenser_overview(dispenser: Dispenser, db: Session) -> dict:
    from models.medication import Medication

    return {
        "id": dispenser.id,
        "device_id": dispenser.device_id,
        "compartments": [
            {
                "compartment_id": c.compartment_id,
                "dispenser_id": c.dispenser_id,
                "medication_id": c.medication_id,
                "medication_name": (
                    db.query(Medication)
                    .filter(Medication.id == c.medication_id)
                    .first()
                    .name
                    if c.medication_id
                    and db.query(Medication)
                    .filter(Medication.id == c.medication_id)
                    .first()
                    is not None
                    else None
                ),
                "quantity": c.quantity,
            }
            for c in dispenser.compartments
        ],
    }


@router.get("/{device_id}", dependencies=[Depends(get_current_user)])
def get_device_overview(device_id: str, db: Session = Depends(get_session)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    dispenser = device.dispenser
    dispenser_data = get_dispenser_overview(dispenser, db) if dispenser else None
    return {
        "id": device.id,
        "senior_id": device.senior_id,
        "status": device.status,
        "last_sync": device.last_sync,
        "dispenser": dispenser_data,
    }


@router.get("/by_senior/{senior_id}", dependencies=[Depends(get_current_user)])
def get_device_by_senior(senior_id: str, db: Session = Depends(get_session)):
    device = db.query(Device).filter(Device.senior_id == senior_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found for this senior")
    dispenser = device.dispenser
    dispenser_data = get_dispenser_overview(dispenser, db) if dispenser else None
    return {
        "id": device.id,
        "senior_id": device.senior_id,
        "status": device.status,
        "last_sync": device.last_sync,
        "dispenser": dispenser_data,
    }
