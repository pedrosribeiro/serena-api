from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from schemas.medication import MedicationRead


class PrescriptionBase(BaseModel):
    description: str
    senior_id: str
    medication_id: str
    doctor_id: str
    dosage: str
    frequency: str
    start_date: str
    end_date: str


class PrescriptionCreate(PrescriptionBase):
    pass


class PrescriptionRead(PrescriptionBase):
    id: str
    medication: MedicationRead
    doctor: Optional[dict] = None

    @validator("start_date", pre=True, always=True)
    def serialize_start_date(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    @validator("end_date", pre=True, always=True)
    def serialize_end_date(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v
