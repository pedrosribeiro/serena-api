from typing import Optional

from pydantic import BaseModel


class SymptomBase(BaseModel):
    name: str
    description: str


class SymptomCreate(SymptomBase):
    pass


class SymptomRead(SymptomBase):
    id: int
    user_id: int
