from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SymptomBase(BaseModel):
    name: str
    description: str
    pain_level: int


class SymptomCreate(SymptomBase):
    senior_id: str  # CPF string de 11 dígitos

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


class SymptomRead(BaseModel):
    id: str
    senior_id: str
    pain_level: int
    description: str
    name: str
    created_at: datetime
