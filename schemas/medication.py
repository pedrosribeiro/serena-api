from typing import Optional

from pydantic import BaseModel


class MedicationBase(BaseModel):
    name: str
    description: Optional[str] = None


class MedicationCreate(MedicationBase):
    pass


class MedicationRead(MedicationBase):
    id: str
