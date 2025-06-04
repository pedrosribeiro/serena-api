from typing import Optional

from pydantic import BaseModel


class CompartmentBase(BaseModel):
    medication_id: str
    quantity: int


class CompartmentCreate(CompartmentBase):
    pass


class CompartmentRead(CompartmentBase):
    compartment_id: str
    dispenser_id: str


class CompartmentUpdate(BaseModel):
    quantity: int
    medication_id: str
