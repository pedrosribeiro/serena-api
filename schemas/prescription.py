from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from schemas.medication import MedicationRead


class PrescriptionBase(BaseModel):
    description: str
    senior_id: str  # CPF string de 11 dígitos
    medication_id: str
    doctor_id: str
    dosage: str
    frequency: str
    start_date: str
    end_date: str

    @classmethod
    def validate_senior_id(cls, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 11):
            raise ValueError(
                "O senior_id deve ser um CPF válido (11 dígitos numéricos)"
            )
        return value

    def __init__(self, **data):
        data["senior_id"] = self.validate_senior_id(data.get("senior_id", ""))
        super().__init__(**data)


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
