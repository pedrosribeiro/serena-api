from typing import List, Optional

from pydantic import BaseModel


class MedicationBase(BaseModel):
    name: str
    dosage: str


class MedicationCreate(MedicationBase):
    pass


class MedicationRead(MedicationBase):
    id: int
    prescription_id: int


class PrescriptionBase(BaseModel):
    description: str


class PrescriptionCreate(PrescriptionBase):
    medications: List[MedicationCreate] = []


class PrescriptionRead(PrescriptionBase):
    id: int
    user_id: int
    medications: List[MedicationRead] = []
