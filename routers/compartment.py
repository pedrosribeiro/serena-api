from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_current_user, get_session
from models.compartment import Compartment
from schemas.compartment import CompartmentCreate, CompartmentRead, CompartmentUpdate

router = APIRouter()


@router.post(
    "/", response_model=CompartmentRead, dependencies=[Depends(get_current_user)]
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
    "/", response_model=List[CompartmentRead], dependencies=[Depends(get_current_user)]
)
def list_compartments(db: Session = Depends(get_session)):
    return db.query(Compartment).all()


@router.get(
    "/{compartment_id}",
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


@router.patch(
    "/{compartment_id}",
    response_model=CompartmentRead,
    dependencies=[Depends(get_current_user)],
)
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
    # Atualiza quantity e medication_id se fornecidos
    if hasattr(update, "quantity") and update.quantity is not None:
        compartment.quantity = update.quantity
    if hasattr(update, "medication_id") and update.medication_id is not None:
        compartment.medication_id = update.medication_id
    db.commit()
    db.refresh(compartment)
    return compartment


@router.put(
    "/{compartment_id}",
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
    "/{compartment_id}", status_code=204, dependencies=[Depends(get_current_user)]
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
