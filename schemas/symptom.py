from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SymptomBase(BaseModel):
    name: str
    description: str
    pain_level: int


class SymptomCreate(SymptomBase):
    senior_id: str


class SymptomRead(BaseModel):
    id: str
    senior_id: str
    pain_level: int
    description: str
    name: str
    created_at: datetime
